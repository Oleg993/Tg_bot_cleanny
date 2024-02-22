import telebot
from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton)
import datetime
from datetime import date, timedelta, datetime
from database import DataBase as db
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


bot = telebot.TeleBot('6748980136:AAEh6eAhemwrxa-oehIo0JzzWsfoF250pxg')
# bot = telebot.TeleBot('6480873823:AAFVK_tC7z2srPOv4iSqllRo8yfO5d709vs')

# client data
client_btns = ['Рассчитать стоимость уборки', 'Мои заказы', 'Мы в соц. сетях', 'Связаться с администратором']
social_media = ['Instagram', 'Facebook']
admin_contact_btns = ['Telegram', 'WhatsApp']
schedule = ['09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00']
text = '''Базовая стоимость уборки объекта состоящего из:
1 комната и 1 санузел - 65 руб.\n
Нажми "ИЗМЕНИТЬ КОЛИЧЕСТВО",
чтобы указать другое количество комнат и сан.узлов, 
либо нажми "РАССЧИТАТЬ УБОРКУ" для уточнения деталей.\n
1 санузел = 1 ванная + 1 туалет
(неважно, совмещенные или раздельные).
Кухня и коридор включены в стоимость.'''
basic_price = 65

user_data = {}
orders = {}

# admin data
admin_btns = ['Нераспределенные заявки', 'Заявки в процессе выполнения', 'График работы клинеров', 'Склад', 'Клинеры',
              'Жалобы от клиентов', 'Отзывы', 'Стат. за вчерашний день', 'Стат. по месяцам', 'Заблокировать клиента']

id = 1924589846

# db().add_admin(1924589846, 'Олег', '+37529 821 89 14')

@bot.message_handler(commands=['start'])
def start(message):
    """Проверяет находился ли в БлэкЛисте, является ли новым пользователем, является ли админом
    :param message: команда /start
    :return: Возвращает клавиатуру Клиент/Админ/Клинер, предлагает регистрацию если новый, шлет подальше если в блэке"""
    if message.text == '/start':
        user_id = message.from_user.id
        orders[user_id] = {}
        orders[user_id]['room_number'] = '1'
        orders[user_id]['bath_number'] = '1'
        orders[user_id]['price'] = 65
        orders[user_id]['price_bath'] = 0
        orders[user_id]['price_room'] = 0
        orders[user_id]['cleaning_time'] = 3
        user_name = message.from_user.first_name
        if not db().is_admin(user_id) and not db().is_cleaner(user_id):
            if not db().is_in_black_list(user_id):
                if not db().is_new(user_id):
                    bot.send_message(message.chat.id, f"Привет {user_name} выбирай.", reply_markup=client_menu())
                else:
                    bot.send_message(message.chat.id, f"Привет {user_name} ты у нас новенький, давай зарегистрируемся!")
                    bot.send_message(message.chat.id, "Введите фамилию, имя, отчество")
                    bot.register_next_step_handler(message, registrator)
            else:
                bot.send_message(message.chat.id, f"Привет {user_name} ты у нас в черном списке, давай до свидания.")

        elif db().is_admin(user_id) and not db().is_cleaner(user_id):
            bot.send_message(message.chat.id, "Панель управления", reply_markup=admin_markup())
        elif db().is_cleaner(user_id) and not db().is_admin(user_id):
            print('cleaner')


def registrator(message):
    """:param message: ФИО из функции start
    :return: регистрирует пользхователя в БД"""
    chat_id = message.chat.id
    if chat_id not in user_data:
        user_data[chat_id] = {}
    if 'user_name' not in user_data[chat_id]:
        user_data[chat_id]['user_name'] = message.text
        bot.send_message(chat_id, "Отлично! Теперь введите свой номер телефона:")
        bot.register_next_step_handler(message, registrator)
    elif 'phone' not in user_data[chat_id]:
        user_data[chat_id]['phone'] = message.text
        bot.send_message(chat_id, "Хорошо! Теперь укажите ваш адрес:\n(г. Минск, ул. Ленина, д. 1, кв.1)")
        bot.register_next_step_handler(message, registrator)
    elif 'address' not in user_data[chat_id]:
        user_data[chat_id]['address'] = message.text
        bot.send_message(chat_id, "Спасибо за регистрацию! Ваши данные приняты.", reply_markup=client_menu())
        data = [chat_id, user_data[chat_id]['user_name'], user_data[chat_id]['phone'], user_data[chat_id]['address']]
        return db().registrator(data)


def client_menu():
    """:return: Возвращает кнопки для панели клиента"""
    markup = InlineKeyboardMarkup()
    for btn in client_btns:
        markup.add(InlineKeyboardButton(btn, callback_data=btn))
    return markup


def connect_to_admin():
    """:return: Возвращает кнопки для связи с админом"""
    markup = InlineKeyboardMarkup()
    for btn in admin_contact_btns:
        if btn == 'Telegram':
            tg_link = f'tg://resolve?domain=cleanny_by'
            markup.add(InlineKeyboardButton(btn, url=tg_link))
        if btn == 'WhatsApp':
            w_app_link = f'https://wa.me/+375447111185'
            markup.add(InlineKeyboardButton(btn, url=w_app_link))
    markup.add(InlineKeyboardButton('Меню', callback_data='menu'))
    return markup


def social_media_menu():
    """:return: Возвращает кнопки для social_media клиента"""
    markup = InlineKeyboardMarkup()
    for btn in social_media:
        if btn == 'Instagram':
            inst_link = f'https://www.instagram.com/bogini_uborka/'
            markup.add(InlineKeyboardButton(btn, url=inst_link))
        if btn == 'Facebook':
            fb_link = f'https://www.facebook.com/cleanny.happy.home/'
            markup.add(InlineKeyboardButton(btn, url=fb_link))
    markup.add(InlineKeyboardButton('Меню', callback_data='menu'))
    return markup


def make_inline_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('ИЗМЕНИТЬ КОЛИЧЕСТВО', callback_data='count'))
    markup.add(InlineKeyboardButton('РАССЧИТАТЬ УБОРКУ', callback_data='calc'))
    markup.add(InlineKeyboardButton('Меню', callback_data='menu'))
    return markup


def change_room_bath():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Комнаты', callback_data='rooms'))
    markup.add(InlineKeyboardButton('Сан. узлы', callback_data='baths'))
    markup.add(InlineKeyboardButton('Назад', callback_data='back'))
    return markup


def change_room_number():
    markup = InlineKeyboardMarkup()
    row1 = []
    for btn in range(1, 5):
        row1.append(InlineKeyboardButton(btn, callback_data=btn))
    row2 = []
    for btn in range(5, 9):
        row2.append(InlineKeyboardButton(btn, callback_data=btn))
    markup.row(*row1)
    markup.row(*row2)
    markup.add(InlineKeyboardButton('Другое количество', callback_data='another_numb'))
    markup.add(InlineKeyboardButton('Назад', callback_data='back_order'))
    return markup


def change_bath_number():
    markup = InlineKeyboardMarkup()
    row1 = []
    for btn in range(1, 5):
        row1.append(InlineKeyboardButton(btn, callback_data=f'{btn} bath'))
    markup.row(*row1)
    markup.add(InlineKeyboardButton('Другое количество', callback_data='another_numb_bath'))
    markup.add(InlineKeyboardButton('Назад', callback_data='back_order'))
    return markup


def get_room_number(message, number):
    chat_id = message.from_user.id
    orders[chat_id]['price_room'] = 0
    orders[chat_id]['price'] = 65 + orders[chat_id]['price_bath']
    if chat_id not in orders:
        orders[chat_id] = {}
    if number.isdigit():
        orders[chat_id]['room_number'] = number
        orders[chat_id]['price_room'] += int(number) * 14 - 14
        orders[chat_id]['price'] += orders[chat_id]['price_room']
        price = orders[chat_id]['price']
        bot.send_message(chat_id, text)
        bot.send_message(chat_id, f'Цена: {price} руб.', reply_markup=make_inline_markup())
    else:
        print('Некорректный формат номера комнаты.')


def get_bath_number(message, number):
    chat_id = message.from_user.id
    orders[chat_id]['price_bath'] = 0
    orders[chat_id]['price'] = 65 + orders[chat_id]['price_room']
    if chat_id not in orders:
        orders[chat_id] = {}
    if number.isdigit():
        orders[chat_id]['bath_number'] = number
        orders[chat_id]['price_bath'] += int(number) * 20 - 20
        orders[chat_id]['price'] += orders[chat_id]['price_bath']
        price = orders[chat_id]['price']
        bot.send_message(chat_id, text)
        bot.send_message(chat_id, f'Цена: {price} руб.', reply_markup=make_inline_markup())
    else:
        print('Некорректный формат номера комнаты.')


def cleaning_schedule():
    markup = InlineKeyboardMarkup()
    row1 = []
    for btn in schedule[:5]:
        row1.append(InlineKeyboardButton(btn, callback_data=btn))
    row2 = []
    for btn in schedule[5:]:
        row2.append(InlineKeyboardButton(btn, callback_data=btn))
    markup.row(*row1)
    markup.row(*row2)
    return markup


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def create_calendar(call):
    chat_id = call.from_user.id
    current_year = date.today().year
    current_month = date.today().month
    current_day = date.today().day
    result, key, step = DetailedTelegramCalendar(min_date=date(current_year, current_month, current_day),
                                                 max_date=date(current_year, current_month + 2, 1) - timedelta(days=1)).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Select {LSTEP[step]}", call.message.chat.id, call.message.message_id, reply_markup=key)
    elif result:
        selected_date = datetime.strptime(str(result), '%Y-%m-%d')
        selected_date_text = selected_date.strftime('%d.%m.%Y')
        if chat_id not in orders:
            print('нет в заказах')
            orders[chat_id] = {}
            orders[chat_id]['room_number'] = '1'
            orders[chat_id]['bath_number'] = '1'
            orders[chat_id]['price'] = 65
            orders[chat_id]['price_bath'] = 0
            orders[chat_id]['price_room'] = 0
            orders[chat_id]['cleaning_time'] = 3
        orders[chat_id]['date'] = selected_date_text
        bot.send_message(chat_id, "Выберите время", reply_markup=cleaning_schedule())


def extra_options():
    """:return: Возвращает кнопки дополнительных опций"""
    options = ["Внутри холодильника", "Внутри духовки", "Внутри кухонных шкафов", "Помоем посуду",
               "Внутри микроволновки", "Погладим белье", "Помоем окна", "Уберем на балконе"]
    markup = InlineKeyboardMarkup()
    row1 = []
    for btn in options[:2]:
        row1.append(InlineKeyboardButton(btn, callback_data=btn))
    row2 = []
    for btn in options[2:4]:
        row2.append(InlineKeyboardButton(btn, callback_data=btn))
    row3 = []
    for btn in options[4:6]:
        row3.append(InlineKeyboardButton(btn, callback_data=btn))
    row4 = []
    for btn in options[6:]:
        row4.append(InlineKeyboardButton(btn, callback_data=btn))
    markup.row(*row1)
    markup.row(*row2)
    markup.row(*row3)
    markup.row(*row4)
    markup.add(InlineKeyboardButton("Далее", callback_data="next_step"))
    return markup


def iron_clothes():
    """:return: Возвращает кнопки глажка белья"""
    markup = InlineKeyboardMarkup()
    row = []
    for btn in range(1, 7):
        row.append(InlineKeyboardButton(str(btn), callback_data=f"{str(btn)}iron_clothes"))
    markup.row(*row)
    markup.add(InlineKeyboardButton("Отменить выбор опции", callback_data="cancel_iron_clothes_order"))
    return markup


def wash_windows():
    """:return: Возвращает кнопки мытья окон"""
    markup = InlineKeyboardMarkup()
    row = []
    for btn in range(1, 7):
        row.append(InlineKeyboardButton(str(btn), callback_data=f"{str(btn)}windows"))
    row2 = []
    for btn in range(7, 13):
        row2.append(InlineKeyboardButton(str(btn), callback_data=f"{str(btn)}windows"))
    markup.row(*row)
    markup.row(*row2)
    markup.add(InlineKeyboardButton("Отменить выбор опции", callback_data="cancel_windows_order"))
    return markup


def clean_balcony():
    """:return: Возвращает кнопки уборки балкона"""
    markup = InlineKeyboardMarkup()
    row = []
    for btn in range(1, 7):
        row.append(InlineKeyboardButton(str(btn), callback_data=f"{str(btn)}balcony"))
    markup.row(*row)
    markup.add(InlineKeyboardButton("Отменить выбор опции", callback_data="cancel_balcony_order"))
    return markup


def address_markup():
    markup = InlineKeyboardMarkup()
    row = []
    row.append(InlineKeyboardButton("Подтвердить", callback_data="take_address"))
    row.append(InlineKeyboardButton("Новый адрес", callback_data="correct_address"))
    markup.row(*row)
    return markup


def user_data_markup():
    markup = InlineKeyboardMarkup()
    row = []
    row.append(InlineKeyboardButton("Подтвердить", callback_data="take_user_data"))
    row.append(InlineKeyboardButton("Новые данные", callback_data="correct_user_data"))
    markup.row(*row)
    return markup


def show_address(user_id):
    address = db().get_user_data(user_id)
    orders[user_id]['order_address'] = address[3]
    return orders[user_id]['order_address']


def correct_address(user_id, message):
    orders[user_id]['order_address'] = message
    db().correct_client_address(orders[user_id]['order_address'], user_id)
    return bot.send_message(user_id, f"Желаете оформить заказ по адресу:\n{show_address(user_id)}",
                            reply_markup=address_markup())


def correct_user_data(message):
    user_id = message.from_user.id
    orders[user_id]['phone_number'] = message.text
    db().correct_client_data(orders[user_id]['user_name'], message.text, user_id)
    new_data = db().get_client_data(user_id)
    bot.send_message(message.chat.id, f"Ваши контактные данные:\n{new_data[1]}\nТелефон: {new_data[2]}",
                     reply_markup=user_data_markup())
    return new_data


def correct_name(message):
    user_id = message.from_user.id
    orders[user_id]['user_name'] = message.text
    bot.send_message(user_id, "Введите номер телефона:\n(пример: +375 29 937 99 92)")
    bot.register_next_step_handler(message, correct_user_data)


def client_orders(user_id):
    markup = InlineKeyboardMarkup()
    orders_list = db().get_order_list(user_id)
    if not orders_list:
        orders_list = 'Список заказов пуст!\nС удовольствием поможем его заполнить! ⬇'
        return orders_list
    if len(orders_list) > 10:
        for order in orders_list[:10]:
            markup.add(InlineKeyboardButton(f"Заказ № {order[0]} от {order[3][:10]}", callback_data=f"order_id{order[0]}"))
    for order in orders_list:
        markup.add(InlineKeyboardButton(f"Заказ № {order[0]} от {order[3][:10]}", callback_data=f"order_id{order[0]}"))
    markup.add(InlineKeyboardButton('Меню', callback_data='menu'))
    return markup


def take_review(message, order_id):
    user_id = message.from_user.id
    current_date = datetime.today().strftime("%d.%m.%Y")
    db().add_comment(message.text, current_date, order_id)
    bot.send_message(message.chat.id, "Коментарий успешно добавлен")
    bot.send_message(message.chat.id, "Список заказов", reply_markup=client_orders(user_id))


# Admin
def admin_markup():
    """:return: Возвращает кнопки для панели админа"""
    markup = InlineKeyboardMarkup()
    for btn in admin_btns:
        markup.add(InlineKeyboardButton(btn, callback_data=btn))
    return markup


def unsigned_orders():
    """:return: Кнопки с нераспределенными заявками"""
    markup = InlineKeyboardMarkup()
    free_orders = db().get_free_orders()
    if not free_orders:
        free_orders = 'Нераспределенных заявок нет!'
        return free_orders
    for idx, order in enumerate(free_orders, start=1):
        markup.add(InlineKeyboardButton(f"{idx}) {order[2]}", callback_data=f'free_order{order[0]}'))
    markup.add(InlineKeyboardButton('Назад', callback_data='admin_back'))
    return markup


@bot.callback_query_handler(func=lambda call: True)
def client_panel(call):
    # print(call.data)
    user_id = call.from_user.id
    chat = call.message.chat.id
    if call.data == 'menu':
        bot.send_message(chat, "Меню", reply_markup=client_menu())

    if call.data == 'back':
        price = orders[chat]['price'] + orders[chat]['price_bath']
        bot.send_message(chat, text)
        bot.send_message(chat, f'Цена: {price} руб.', reply_markup=make_inline_markup())

    if call.data == 'back_order':
        bot.send_message(chat, "Выберите категорию:", reply_markup=change_room_bath())

    if call.data == 'Рассчитать стоимость уборки':
        bot.send_message(chat, text)
        bot.send_message(chat, 'Цена: 65 руб.', reply_markup=make_inline_markup())

    if call.data == 'count':
        bot.send_message(chat, "Выберите категорию:", reply_markup=change_room_bath())

    if call.data == 'rooms':
        bot.send_message(chat, "Укажите необходимое количество:", reply_markup=change_room_number())

    if call.data == 'baths':
        bot.send_message(chat, "Укажите необходимое количество:", reply_markup=change_bath_number())

    if call.data in [str(i) for i in range(1, 9)]:
        get_room_number(call, call.data)

    if call.data == 'another_numb':
        bot.send_message(chat, "Впишите желаемое количество комнат (цифрой):")
        bot.register_next_step_handler(call.message, lambda message: get_room_number(message, message.text))

    if call.data in ['1 bath', '2 bath', '3 bath', '4 bath']:
        get_bath_number(call, call.data[:-5])

    if call.data == 'another_numb_bath':
        bot.send_message(chat, "Выберите количество сан. узлов:", reply_markup=change_bath_number())
        bot.register_next_step_handler(call.message, lambda message: get_room_number(message, message.text))

    if call.data == 'calc':
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Чек-лист",
                                        url='https://drive.google.com/file/d/1gH8ogErgeWSeqIPhM9XQVPitbmzHxG1v/view'))

        bot.send_message(chat, """Сейчас я задам несколько дополнительных вопросов,
для расчета окончательной стоимости уборки\nи выбора дополнительных опций,\nесли они вам необходимы
\nИз чего состоит базавая уборка: чек-лист ⬇️""", reply_markup=markup)

        current_year = date.today().year
        current_month = date.today().month
        current_day = date.today().day
        calendar, step = DetailedTelegramCalendar(min_date=date(current_year, current_month, current_day),
                                                  max_date=date.today() + timedelta(weeks=1), locale='ru').build()
        bot.send_message(chat, f"Выберите дату", reply_markup=calendar)

    if call.data in schedule:
        orders[user_id]['selected_time'] = call.data
        bot.send_message(chat, f"""Желаемая дата уборки:
{orders[user_id]['date']}, {orders[user_id]['selected_time']} часов,\nВремя уборки: {orders[user_id]['cleaning_time']}
Стандартная стоимость: 65 руб.\nК оплате: {orders[user_id]['price']}""")
        bot.send_message(chat, "Дополнительные опции:", reply_markup=extra_options())

    if call.data == 'Внутри холодильника':
        if 'fridge' in orders[user_id]:
            orders[user_id]['fridge'] = - 1
            orders[user_id]['cleaning_time'] -= 1
        else:
            orders[user_id]['fridge'] = 1
            orders[user_id]['cleaning_time'] += 1
        orders[user_id]['price'] += orders[user_id]['fridge'] * 25

        bot.send_message(chat, f"""Желаемая дата уборки:
{orders[user_id]['date']}, {orders[user_id]['selected_time']} часов,
Длительность уборки: {orders[user_id]['cleaning_time']} ч.\nСтандартная стоимость: 65 руб.
К оплате: {orders[user_id]['price']}""")
        bot.send_message(chat, "Дополнительные опции:", reply_markup=extra_options())

    if call.data == 'Внутри духовки':
        if 'stove' in orders[user_id]:
            orders[user_id]['stove'] = - 1
            orders[user_id]['cleaning_time'] -= 1
        else:
            orders[user_id]['stove'] = 1
            orders[user_id]['cleaning_time'] += 1
        orders[user_id]['price'] += orders[user_id]['stove'] * 25

        bot.send_message(chat, f"""Желаемая дата уборки:
{orders[user_id]['date']}, {orders[user_id]['selected_time']} часов,
Длительность уборки: {orders[user_id]['cleaning_time']} ч.\nСтандартная стоимость: 65 руб.
К оплате: {orders[user_id]['price']}""")
        bot.send_message(chat, "Дополнительные опции:", reply_markup=extra_options())

    if call.data == 'Внутри кухонных шкафов':
        if 'inside_cabinets' in orders[user_id]:
            orders[user_id]['inside_cabinets'] = - 1
            orders[user_id]['cleaning_time'] -= 1
        else:
            orders[user_id]['inside_cabinets'] = 1
            orders[user_id]['cleaning_time'] += 1
        orders[user_id]['price'] += orders[user_id]['inside_cabinets'] * 25

        bot.send_message(chat, f"""Желаемая дата уборки:
{orders[user_id]['date']}, {orders[user_id]['selected_time']} часов,
Длительность уборки: {orders[user_id]['cleaning_time']} ч.\nСтандартная стоимость: 65 руб.
К оплате: {orders[user_id]['price']}""")
        bot.send_message(chat, "Дополнительные опции:", reply_markup=extra_options())

    if call.data == 'Помоем посуду':
        if 'dishes' in orders[user_id]:
            orders[user_id]['dishes'] = - 1
            orders[user_id]['cleaning_time'] -= 0.5
        else:
            orders[user_id]['dishes'] = 1
            orders[user_id]['cleaning_time'] += 0.5
        orders[user_id]['price'] += orders[user_id]['dishes'] * 10

        bot.send_message(chat, f"""Желаемая дата уборки:
{orders[user_id]['date']}, {orders[user_id]['selected_time']} часов,
Длительность уборки: {orders[user_id]['cleaning_time']} ч.\nСтандартная стоимость: 65 руб.
К оплате: {orders[user_id]['price']}""")
        bot.send_message(chat, "Дополнительные опции:", reply_markup=extra_options())

    if call.data == 'Внутри микроволновки':
        if 'microwave' in orders[user_id]:
            orders[user_id]['microwave'] = - 1
            orders[user_id]['cleaning_time'] -= 0.5
        else:
            orders[user_id]['microwave'] = 1
            orders[user_id]['cleaning_time'] += 0.5
        orders[user_id]['price'] += orders[user_id]['microwave'] * 20

        bot.send_message(chat, f"""Желаемая дата уборки:
{orders[user_id]['date']}, {orders[user_id]['selected_time']} часов,
Длительность уборки: {orders[user_id]['cleaning_time']} ч.\nСтандартная стоимость: 65 руб.
К оплате: {orders[user_id]['price']}""")
        bot.send_message(chat, "Дополнительные опции:", reply_markup=extra_options())

    if call.data == 'Погладим белье':
        bot.send_message(chat, "Выберите количество часов:\n(один час - 20р.)", reply_markup=iron_clothes())

    if call.data[-12:] == 'iron_clothes':
        if 'iron_clothes' in orders[user_id]:
            orders[user_id]['cleaning_time'] -= orders[user_id]['iron_clothes']
            orders[user_id]['price'] -= (orders[user_id]['iron_clothes'] * 20)
        orders[user_id]['iron_clothes'] = int(call.data[:-12])
        orders[user_id]['cleaning_time'] += orders[user_id]['iron_clothes']
        orders[user_id]['price'] += orders[user_id]['iron_clothes'] * 20
        bot.send_message(chat, f"""Желаемая дата уборки:
{orders[user_id]['date']}, {orders[user_id]['selected_time']} часов,
Длительность уборки: {orders[user_id]['cleaning_time']} ч.\nСтандартная стоимость: 65 руб.
К оплате: {orders[user_id]['price']}""")
        bot.send_message(chat, "Дополнительные опции:", reply_markup=extra_options())

    if call.data == 'cancel_iron_clothes_order':
        if 'iron_clothes' in orders[user_id]:
            orders[user_id]['cleaning_time'] -= orders[user_id]['iron_clothes']
            orders[user_id]['price'] -= orders[user_id]['iron_clothes'] * 20
            orders[user_id]['iron_clothes'] = 0
        bot.send_message(chat, f"""Желаемая дата уборки:
{orders[user_id]['date']}, {orders[user_id]['selected_time']} часов,
Длительность уборки: {orders[user_id]['cleaning_time']} ч.\nСтандартная стоимость: 65 руб.
К оплате: {orders[user_id]['price']}""")
        bot.send_message(chat, "Дополнительные опции:", reply_markup=extra_options())

    if call.data == 'Помоем окна':
        bot.send_message(chat, "Выберите количество окон:\n(одно окно - 15р.)", reply_markup=wash_windows())

    if call.data[-7:] == 'windows':
        if 'windows' in orders[user_id]:
            orders[user_id]['cleaning_time'] -= (orders[user_id]['windows'] / 2)
            orders[user_id]['price'] -= (orders[user_id]['windows'] * 15)
        orders[user_id]['windows'] = int(call.data[:-7])
        orders[user_id]['cleaning_time'] += (orders[user_id]['windows'] / 2)
        orders[user_id]['price'] += (orders[user_id]['windows'] * 15)
        bot.send_message(chat, f"""Желаемая дата уборки:
{orders[user_id]['date']}, {orders[user_id]['selected_time']} часов,
Длительность уборки: {orders[user_id]['cleaning_time']} ч.\nСтандартная стоимость: 65 руб.
К оплате: {orders[user_id]['price']}""")
        bot.send_message(chat, "Дополнительные опции:", reply_markup=extra_options())

    if call.data == 'cancel_windows_order':
        if 'windows' in orders[user_id]:
            orders[user_id]['cleaning_time'] -= (orders[user_id]['windows'] / 2)
            orders[user_id]['price'] -= (orders[user_id]['windows'] * 15)
            orders[user_id]['windows'] = 0
        bot.send_message(chat, f"""Желаемая дата уборки:
{orders[user_id]['date']}, {orders[user_id]['selected_time']} часов,
Длительность уборки: {orders[user_id]['cleaning_time']} ч.\nСтандартная стоимость: 65 руб.
К оплате: {orders[user_id]['price']}""")
        bot.send_message(chat, "Дополнительные опции:", reply_markup=extra_options())

    if call.data == 'Уберем на балконе':
        bot.send_message(chat, "Выберите количество балконов:\n(один балкон - 20р.)", reply_markup=clean_balcony())

    if call.data[-7:] == 'balcony':
        if 'balcony' in orders[user_id]:
            orders[user_id]['cleaning_time'] -= orders[user_id]['balcony']
            orders[user_id]['price'] -= (orders[user_id]['balcony'] * 20)
        orders[user_id]['balcony'] = int(call.data[:-7])
        orders[user_id]['cleaning_time'] += orders[user_id]['balcony']
        orders[user_id]['price'] += orders[user_id]['balcony'] * 20
        bot.send_message(chat, f"""Желаемая дата уборки:
{orders[user_id]['date']}, {orders[user_id]['selected_time']} часов,
Длительность уборки: {orders[user_id]['cleaning_time']} ч.\nСтандартная стоимость: 65 руб.
К оплате: {orders[user_id]['price']}""")
        bot.send_message(chat, "Дополнительные опции:", reply_markup=extra_options())

    if call.data == 'cancel_balcony_order':
        if 'balcony' in orders[user_id]:
            orders[user_id]['cleaning_time'] -= orders[user_id]['balcony']
            orders[user_id]['price'] -= (orders[user_id]['balcony'] * 20)
            orders[user_id]['balcony'] = 0
        bot.send_message(chat, f"""Желаемая дата уборки:
{orders[user_id]['date']}, {orders[user_id]['selected_time']} часов,
Длительность уборки: {orders[user_id]['cleaning_time']} ч.\nСтандартная стоимость: 65 руб.
К оплате: {orders[user_id]['price']}""")
        bot.send_message(chat, "Дополнительные опции:", reply_markup=extra_options())

    if call.data == 'next_step':
        bot.send_message(chat, f"Желаете оформить заказ по адресу:\n{show_address(user_id)}",
                         reply_markup=address_markup())

    if call.data == 'correct_address':
        bot.send_message(chat, "Введите новый адрес:\n(г.Минск, ул. Ленина, д. 1, кв.1)")
        bot.register_next_step_handler(call.message, lambda message: correct_address(user_id, message.text))

    if call.data == 'take_address':
        data = db().get_user_data(user_id)
        name, phone = data[1], data[2]
        bot.send_message(chat, f"Ваши контактные данные:\n{name}\nТелефон: {phone}",
                         reply_markup=user_data_markup())

    if call.data == 'correct_user_data':
        bot.send_message(chat, "Введите ФИО:\n(пример: Пушкин Александр Сергеевич)")
        bot.register_next_step_handler(call.message, correct_name)

    if call.data == 'take_user_data':
        data = db().get_client_data(user_id)
        name, phone, address = data[1], data[2], data[3]

        markup = InlineKeyboardMarkup()
        row = []
        row.append(InlineKeyboardButton("Оформить заказ", callback_data="finish_order"))
        row.append(InlineKeyboardButton("Отменить заказ", callback_data="cancel_order"))
        markup.row(*row)

        bot.send_message(chat, f"""Дата уборки:
{orders[user_id]['date']}, {orders[user_id]['selected_time']} часов,
Длительность уборки: {orders[user_id]['cleaning_time']} ч.\nК оплате: {orders[user_id]['price']}\n
Ваши контактные данные:\n{name}\nТелефон: {phone}\nАдрес: {address}""", reply_markup=markup)

    if call.data == 'finish_order':
        print(orders[user_id])
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('Меню', callback_data='menu'))
        order_date = datetime.today().strftime("%d.%m.%Y")
        status = 'Обрабатывается'
        date_time_for_order = f"{orders[user_id]['date']}, {orders[user_id]['selected_time']}"
        address = show_address(user_id)
        client_id = user_id
        staff_id = None
        room_count = orders[user_id]['room_number']
        bathroom_count = orders[user_id]['bath_number']
        def_values = {'fridge': 0, 'stove': 0, 'cabinets': 0, 'dishes': 0, 'microwave': 0, 'clothes': 0,
                          'windows': 0, 'balcony': 0}
        for key in def_values:
            if key in orders[user_id]:
                def_values[key] = orders[user_id][key]
        discount = None
        price = orders[user_id]['price']

        db().add_data_to_orders([order_date, status, date_time_for_order, address, client_id, staff_id, room_count,
                                 bathroom_count, def_values['fridge'], def_values['stove'], def_values['cabinets'],
                                 def_values['dishes'], def_values['microwave'], def_values['clothes'],
                                 def_values['windows'], def_values['balcony'], discount, price])
        bot.send_message(chat, """Ваша заявка принята!\nВ ближайшее время с Вами свяжется наш администратор,
для подтверждения заказа, либо Вы получите сообщение о подтверждении в Телеграм.""", reply_markup=markup)

    if call.data == 'Мои заказы':
        orders_markup = client_orders(user_id)
        if isinstance(orders_markup, str):
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('Меню', callback_data='menu'))
            bot.send_message(chat, orders_markup, reply_markup=markup)
        else:
            bot.send_message(chat, f"Список заказов:\n\n", reply_markup=client_orders(user_id))

    if call.data[:8] == 'order_id':
        order_data = db().get_order(int(call.data[8:]))
        comment = db().get_comment(order_data[-1])
        if not comment:
            comment = 'Отзыв отсутствует.'

        markup = InlineKeyboardMarkup()
        if call.data[8:] == db().get_last_order(user_id):
            markup.add(InlineKeyboardButton('Оставить отзыв', callback_data=f'client_review{call.data[8:]}'))
            markup.add(InlineKeyboardButton('Назад', callback_data='Мои заказы'))
        else:
            markup.add(InlineKeyboardButton('Назад', callback_data='Мои заказы'))
        bot.send_message(chat, f"""Заказ № {call.data[8:]}\nДата: {order_data[1]} часов\nАдрес: {order_data[2]}\n
Клинер: {order_data[3]}\nСтатус исполнения: {order_data[0]}\nОбщая стоимоcть:{order_data[4]}
\nОтзыв:\n{comment}""", reply_markup=markup)

    if call.data[:13] == 'client_review':
        order_id = int(call.data[13:])
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('Отмена', callback_data='review_cancel'))
        bot.send_message(chat, "Оставьте свой отзыв ⬇", reply_markup=markup)
        bot.register_next_step_handler(call.message, take_review, order_id)

    if call.data == 'review_cancel':
        bot.clear_step_handler_by_chat_id(chat)
        bot.send_message(chat, f"Список заказов:\n\n", reply_markup=client_orders(user_id))

    if call.data == 'Мы в соц. сетях':
        bot.send_message(chat, "Будем рады видеть Вас в качестве нашего подписчика:", reply_markup=social_media_menu())

    if call.data == 'Связаться с администратором':
        bot.send_message(chat, "Выбирай", reply_markup=connect_to_admin())

    # admin
    if call.data == 'admin_back':
        bot.send_message(chat, "Панель управления", reply_markup=admin_markup())

    if call.data == 'Нераспределенные заявки':
        free_orders_markup = unsigned_orders()
        if isinstance(free_orders_markup, str):
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('Назад', callback_data='admin_back'))
            bot.send_message(chat, free_orders_markup, reply_markup=markup)
        else:
            bot.send_message(chat, f"Нераспределенные заявки:\n\n", reply_markup=free_orders_markup)

    if call.data[:10] == 'free_order':
        order_id = int(call.data[10:])
        ord_data = db().get_free_order_data(order_id)
        client_data = db().get_client_data(ord_data[5])
        client = '\n'.join(str(item) for item in client_data)
        bot.send_message(chat, f"""Номер заказа: {ord_data[0]}\nКогда поступил заказ{ord_data[1]}\nСтатус{ord_data[2]}
Дата начала уборки:{ord_data[3]}\nАдрес: {ord_data[4]}\nКлиент:\n{client}\nКомнаты: {ord_data[6]}\nСан.узлы: {ord_data[7]}
Внутри холодильника: {ord_data[7]}\nВнутри духовки: {ord_data[8]}\nВнутри духовки: {ord_data[8]}
Внутри кухонных шкафов: {ord_data[9]}\nПомоем посуду: {ord_data[10]}\nВнутри микроволновки: {ord_data[11]}
Погладим белье: {ord_data[12]}\nПомоем окна: {ord_data[13]}\nУберем на балконе: {ord_data[14]}""")


print('ready')
bot.polling(none_stop=True)

