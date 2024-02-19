import telebot
from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton)
import os
import datetime
from datetime import date, timedelta, datetime
from database import DataBase as db
import calendar


# bot = telebot.TeleBot('6748980136:AAEh6eAhemwrxa-oehIo0JzzWsfoF250pxg')
bot = telebot.TeleBot('6480873823:AAFVK_tC7z2srPOv4iSqllRo8yfO5d709vs')


client_btns = ['Рассчитать стоимость уборки', 'Мои заказы', 'Мы в соц. сетях', 'Связаться с администратором']
social_media = ['Instagram', 'Facebook']
admin_contact_btns = ['Telegram', 'WhatsApp']
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


@bot.message_handler(commands=['start'])
def start(message):
    """Проверяет находился ли в БлэкЛисте, является ли новым пользователем, является ли админом
    :param message: команда /start
    :return: Возвращает клавиатуру Клиент/Админ/Клинер, предлагает регистрацию если новый, шлет подальше если в блэке"""
    if message.text == '/start':
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        if not db().is_in_black_list(user_id):
            if not db().is_new(user_id):
                if not db().is_admin(user_id) and not db().is_cleaner(user_id):
                    bot.send_message(message.chat.id, f"Привет {user_name} выбирай.", reply_markup=client_menu())
                else:
                    print('admin')
                    # bot.send_message(message.chat.id, f"Привет {user_name} выбирай.", reply_markup=first_markup())
            else:
                bot.send_message(message.chat.id, f"Привет {user_name} ты у нас новенький, давай зарегистрируемся!?")
                bot.send_message(message.chat.id, "Введите имя, фамилию, отчество")
                bot.register_next_step_handler(message, registrator)
        else:
            bot.send_message(message.chat.id, f"Привет {user_name} ты у нас в черном списке, давай до свидания.")


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
        bot.send_message(chat_id, "Спасибо за регистрацию! Ваши данные приняты.")
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
        price = orders[chat_id]['price'] + orders[chat_id]['price_room']
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
        price = orders[chat_id]['price'] + orders[chat_id]['price_bath']
        bot.send_message(chat_id, text)
        bot.send_message(chat_id, f'Цена: {price} руб.', reply_markup=make_inline_markup())
    else:
        print('Некорректный формат номера комнаты.')


def create_calendar():
    markup = InlineKeyboardMarkup()
    year = datetime.now().year
    month = datetime.now().month
    cal = calendar.monthcalendar(year, month)

    for week in cal:
        row = []
        for day in week:
            if day != 0:
                row.append(InlineKeyboardButton(str(day), callback_data=f'day_{day}'))
            else:
                row.append(InlineKeyboardButton("", callback_data="empty"))
        markup.row(*row)

    next_month = month + 1
    if next_month > 12:
        next_month = 1
        year += 1

    markup.add(InlineKeyboardButton("➡️ Следующий месяц", callback_data=f'next_month_{next_month}'))

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
        orders[user_id] = {}
        orders[user_id]['room_number'] = '1'
        orders[user_id]['bath_number'] = '1'
        orders[user_id]['price'] = 65
        orders[user_id]['price_bath'] = 0
        orders[user_id]['price_room'] = 0

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
        bot.send_message(chat, "Выберите дату:", reply_markup=create_calendar())




    if call.data == 'Мы в соц. сетях':
        bot.send_message(chat, "Будем рады видеть Вас в качестве нашего подписчика:", reply_markup=social_media_menu())

    if call.data == 'Связаться с администратором':
        bot.send_message(chat, "Выбирай", reply_markup=connect_to_admin())


print('ready')
bot.polling(none_stop=True)

