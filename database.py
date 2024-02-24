from datetime import date
import sqlite3
import telebot

bot = telebot.TeleBot('6748980136:AAEh6eAhemwrxa-oehIo0JzzWsfoF250pxg')


class DataBase:
    # client
    def __init__(self):
        self.db_file = 'cleanny.db'

    def is_in_black_list(self, user_id):
        """проверка пользователь в блэке или нет
        :param user_id: id пользователя
        :return: True - в блэке, False - нет"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT blacklisted FROM Clients WHERE id == ?", [user_id])
                result = cursor.fetchone()
                return result[0] == '1' if result is not None else False
        except sqlite3.Error as e:
            print(f"Произошла ошибка: {e}")
            return False

    def is_admin(self, user_id):
        """проверяем является ли админом
        :param user_id: id пользователя
        :return: True - admin, False - не админ"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT id FROM Admins WHERE id == ?", [user_id])
                result = cursor.fetchone()
                return result is not None
        except sqlite3.Error as e:
            print(f"Произошла ошибка: {e}")
            return False

    def is_cleaner(self, user_id):
        """проверяем является ли клинером
        :param user_id: id пользователя
        :return: True - клинер, False - не клинер"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT id FROM Staff WHERE id == ?", [user_id])
                result = cursor.fetchone()
                return True if result is not None else False
        except sqlite3.Error as e:
            print(f"Произошла ошибка: {e}")
            return False

    def is_new(self, user_id):
        """проверка новый пользователь или нет
        :param user_id: id пользователя
        :return: True - новый, False - есть в базе"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT id FROM Clients WHERE id == ?", [user_id])
                result = cursor.fetchone()
                return True if result is None else False
        except sqlite3.Error as e:
            print(f"Произошла ошибка: {e}")
            return True

    def get_user_data(self, user_id):
        """ Получение данных пользователя
        :param user_id: id пользователя
        :return: Возвращает данные пользователя в виде кортежа"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM Clients where id = ?", [user_id])
                result = cursor.fetchone()
                return False if result is None else result
        except sqlite3.Error as e:
            print(f"Ошибка при получении информации о пользователе: {e}")
            return False

    def show_clients(self):
        """Отображение списка имеющихся клиентов
        :return: возвращаем список кортежей [(name, id, block_status)]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT name, id, blacklisted FROM Clients")
                data = cursor.fetchall()
                return data if len(data) != 0 else False
        except sqlite3.Error as e:
            print(f"Не удалось получить список администраторов: {e}")
            return False

    def registrator(self, client_data):
        """принимает список данных и добавляет пользователя в БД
        :param client_data: [id, name, contact_info, address]
        :return:True если регистрация прошла успешно"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("INSERT INTO Clients(id, name, phone, address) VALUES (?, ?, ?, ?)", client_data)
                return cursor.rowcount == 1
        except sqlite3.Error as e:
            print(f"Ошибка при выполнении регистраиции: {e}")
            return False

    def get_order_list(self, client_id):
        """возвращает список всех заказов клиента
        :param client_id: id клиента
        :return: список id заказов [1, 2]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM Orders WHERE client_id = ?", [client_id])
                result = cursor.fetchall()
                return False if len(result) == 0 else [i for i in result]
        except sqlite3.Error as e:
            print(f"Не удалось загрузить список товаров категории: {e}")
            return False

    def get_order(self, order_id):
        """возвращает данные по заказу
        :param order_id: id заказа
        :return: список данных заказа [id, дата, имя Клинера, кол-во комнат, кол-во уборных, доп.услуги, цена]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT staff_id FROM Orders WHERE id = ?", [order_id])
                staff_id = cursor.fetchone()[0]
                if staff_id == 'Еще не назначен':
                    cursor.execute("SELECT status, date_time, address, price, id FROM Orders WHERE Orders.id = ?",
                                   [order_id])
                    result = list(cursor.fetchone())
                    result.append('Еще не назначен')
                    return False if result is None else result
                else:
                    cursor.execute("""
                    SELECT Orders.status, Orders.date_time, Orders.address, Orders.price, Orders.id, Staff.name
                    FROM Orders 
                    JOIN Staff ON Orders.staff_id = Staff.id 
                    WHERE Orders.id = ?""", [order_id])
                    result = cursor.fetchone()
                    return False if result is None else result
        except sqlite3.Error as e:
            print(f"Не удалось загрузить список заказов: {e}")
            return False

    def get_last_order(self, client_id):
        """возвращает id последнего заказа
        :param client_id: id заказа
        :return: id последнего заказа"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT MAX(id), status FROM Orders WHERE client_id = ? ", [client_id])
                result = cursor.fetchone()
                cursor.execute("SELECT order_id FROM Reviews WHERE order_id = ?", [result[0]])
                is_review = cursor.fetchone()
                if result[1] == 'Уборка завершена':
                    return str(result[0]) if is_review is None else False
                else:
                    return False
        except sqlite3.Error as e:
            print(f"Не удалось загрузить список заказов: {e}")
            return False

    def get_social_media(self, status):
        """возвращает список ссылок на соц. сети или мессенджеров
        :param status: 0 - соц. сети, 1 - мессенджеры
        :return: список ссылок [ссылка, ссылка]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM Social_media WHERE messanger_or_link = ?", [status])
                result = cursor.fetchall()
                return False if len(result) == 0 else [i[0] for i in result]
        except sqlite3.Error as e:
            print(f"Не удалось загрузить список контактов: {e}")
            return False

    def add_data_to_orders(self, data):
        """добавление данных в Orders
        :param data: [order_date, status, address, client_id, staff_id, discount, room_count, bathroom_count,
        other_details, order_time]
        :return: True - добавлено, False - нет"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("""INSERT INTO Orders (order_date, status, date_time, address, client_id, staff_id,
                room_count, bathroom_count, fridge, stove, cabinets, dishes, microwave, clothes, windows, balcony, 
                discount, price, order_time) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                               [*data])
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Не удалось добавить данные: {e}")
            return False

    def get_client_data(self, client_id):
        """Отображение даных клиента
        :return: возвращаем список данных [id, имя, контактные данные, адрес)]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT id, name, phone, address FROM Clients WHERE id= ?", [client_id])
                data = cursor.fetchone()
                return data if not None else False
        except sqlite3.Error as e:
            print(f"Не удалось получить данные клиента: {e}")
            return False

    def correct_client_address(self, address, client_id):
        """изменение адреса клиента
        :param address: новый адрес
        :param client_id: id клиента
        :return:True если изменения внесены успешно иначе False"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("""UPDATE Clients SET address = ? WHERE id = ?""", [address, client_id])
                return cursor.rowcount == 1
        except sqlite3.Error as e:
            print(f"Ошибка при изменении данных: {e}")
            return False

    def correct_client_data(self, client_name, client_phone, client_id):
        """изменение данных клиента
        :param client_name: name
        :param client_phone: phone
        :param client_id: id клиента
        :return:True если изменения внесены успешно иначе False"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("""UPDATE Clients SET name = ?, phone = ? WHERE id = ?""",
                               [client_name, client_phone, client_id])
                return cursor.rowcount == 1
        except sqlite3.Error as e:
            print(f"Ошибка при изменении данных: {e}")
            return False

    def add_comment(self, comment, current_date, order_id):
        """Доавление отзыва
        :param comment: текст комментария
        :param current_date: дата комментария
        :param order_id: номер заказа
        :return:True если добавлен успешно"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("INSERT INTO Reviews(review_text, date, order_id) VALUES (?, ?, ?)",
                               [comment, current_date, order_id])
                return cursor.rowcount == 1
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении отзыва: {e}")
            return False

    def get_comment(self, order_id):
        """возвращает отзыв по заказу
        :param order_id: id заказа
        :return: отзыв по заказу"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT review_text FROM Reviews WHERE order_id = ?", [order_id])
                result = cursor.fetchone()
                return False if result is None else result[0]
        except sqlite3.Error as e:
            print(f"Не удалось загрузить отзыв: {e}")
            return False

    # admin

    def add_admin(self, user_id, name, phone):
        """Доавление админа
        :param user_id: admin id
        :param name: admin name
        :param phone: admin phone
        :return:True если добавлен успешно"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("INSERT INTO Admins(id, name, phone) VALUES (?, ?, ?)", [user_id, name, phone])
                return cursor.rowcount == 1
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении администратора: {e}")
            return False

    def get_free_orders(self):
        """возвращает список нераспределенных заявок
        :return: список заказов [[id, date ...] [id, date ...]]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT id, address, date_time FROM Orders WHERE status = ?", ['Обрабатывается'])
                result = cursor.fetchall()
                return False if len(result) == 0 else result
        except sqlite3.Error as e:
            print(f"Не удалось загрузить список свободных заявок: {e}")
            return False

    def get_free_order_data(self, order_id):
        """возвращает данные по заказу
        :param order_id: id заказа
        :return: все данные по заказу"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM Orders WHERE id = ?", [order_id])
                result = cursor.fetchone()
                return False if result is None else result
        except sqlite3.Error as e:
            print(f"Не удалось загрузить данные заказа: {e}")
            return False

    # cleaner

    def add_cleaner(self, user_id, name, phone, worked_hours_current_week, worked_hours_day, work_schedule):
        """Доавление клинера
        :param user_id: admin id
        :param name: admin name
        :param phone: admin phone
        :param worked_hours_current_week: отработано часов в текущей неделе
        :param worked_hours_day: отработано часов за день
        :param work_schedule: работает сегодня или нет
        :return:True если добавлен успешно"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("""INSERT INTO Staff(id, name, contact_info, worked_hours_current_week, 
                worked_hours_day, work_schedule)
                               VALUES (?, ?, ?, ?, ?, ?)""",
                               [user_id, name, phone, worked_hours_current_week, worked_hours_day, work_schedule])
                return cursor.rowcount == 1
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении клинера: {e}")
            return False

    def get_list_of_cleaners(self, status=None):
        """возвращает список клинеров
        :param status: 1 - доступные клинеры, None - все клинеры
        :return: Список клинеров[[id, name, phone, week_hours, status]]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                if not status:
                    cursor.execute("SELECT * FROM Staff")
                    result = cursor.fetchall()
                else:
                    cursor.execute("SELECT * FROM Staff WHERE work_schedule = ?", [status])
                    result = cursor.fetchall()
                return False if len(result) == 0 else result
        except sqlite3.Error as e:
            print(f"Не удалось загрузить список клинеров: {e}")
            return False

    def make_cleaner_to_order(self, order_id, cleaner_id, order_time):
        """возвращает Назначает уборщика на заявку
        :param cleaner_id: id клинера
        :param order_id: id заявки
        :param order_time: время исполнения заказа
        :return: True - назначен, False - нет"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("UPDATE Orders SET staff_id = ? WHERE id = ?", [cleaner_id, order_id])
                if cursor.rowcount > 0:
                    cursor.execute("SELECT worked_hours_day, worked_hours_current_week FROM Staff WHERE id = ?",
                                   [cleaner_id])
                    hours_day = cursor.fetchone()
                    if int(hours_day[0]) > 7 or int(hours_day[1]) > 37:
                        cursor.execute("UPDATE Staff SET work_schedule = ? WHERE id = ?", [0, cleaner_id])
                        cursor.execute("UPDATE Orders SET status = ? WHERE staff_id = ?", ['Клинер назначен', cleaner_id])
                        return cursor.rowcount > 0
                    else:
                        new_hours_day = int(hours_day[0]) + int(order_time)
                        new_hours_week = int(hours_day[1]) + int(order_time)
                        cursor.execute("UPDATE Staff SET worked_hours_day = ?, worked_hours_current_week = ? WHERE id = ?",
                                       [new_hours_day, new_hours_week, cleaner_id])
                        cursor.execute("UPDATE Orders SET status = ? WHERE staff_id = ?", ['Клинер назначен', cleaner_id])
                        return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Не удалось назначить клинера: {e}")
            return False

    def get_orders_in_run(self):
        """возвращает список незавершенных заявок
           :return: Список заявок[(id, order_date, ...), (id, order_date, ...)]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM Orders WHERE status != ?", ['Уборка завершена'])
                result = cursor.fetchall()
                return False if len(result) == 0 else result
        except sqlite3.Error as e:
            print(f"Не удалось загрузить список текущих заявок: {e}")
            return False

    def delete_cleaner(self, cleaner_id):
        """удаляет клнира
           :return: True - удален, False - нет"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("DELETE FROM Staff WHERE id= ?", [cleaner_id])
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Не удалось удалить клинера: {e}")
            return False

    def get_cleaner_orders(self, cleaner_id):
        """возвращает список последних 5 заказов клинера, в которых есть отзывы
          :return: Список [(id, date_time), (id, date_time)]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT id, date_time FROM Orders WHERE staff_id = ?", [cleaner_id])
                result = cursor.fetchall()
                return False if len(result) == 0 else result
        except sqlite3.Error as e:
            print(f"Не удалось загрузить список исполненных клинером заявок: {e}")
            return False

    def get_cleaner_review_card(self, order_id):
        """возвращает по конкретному отзыву
          :return: Список [Clients.name, Clients.phone, Clients.address, Reviews.review_text, Orders.staff_id]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT review_text FROM Reviews WHERE order_id = ?", [order_id])
                review_text = cursor.fetchone()
                cursor.execute("""SELECT Clients.name, Clients.phone, Clients.address, Orders.staff_id
                FROM Orders
                JOIN Clients ON Orders.client_id = Clients.id 
                WHERE Orders.id = ?""", [order_id])
                result = list(cursor.fetchone())
                if review_text:
                    result.append(review_text[0])
                else:
                    result.append('Коментарий отсутствует')
                return False if result is None else result
        except sqlite3.Error as e:
            print(f"Не удалось загрузить список исполненных клинером заявок: {e}")
            return False

    def delete_review(self, order_id):
        """удаляет конкретный отзыв
        :param order_id - id заказа
        :return: True - удален, False - нет"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("DELETE FROM Reviews WHERE order_id= ?", [order_id])
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Не удалось удалить отзыв: {e}")
            return False

    def get_clients_list(self):
        """возвращает список клиентов текстом
        :return: Список [(id, name, address)]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT id, name, phone, blacklisted FROM Clients")
                result = cursor.fetchall()
                clients = [f'ID: {item[0]}, {item[1]}, {"-- Не заблокирован" if item[3] == 0 else "-- Заблокирован"}'
                           for item in result]
                result = '\n'.join(clients)
                return False if len(result) == 0 else result
        except sqlite3.Error as e:
            print(f"Не удалось загрузить список клиентов: {e}")
            return False

###############################
    def add_client(self, user_id, name, phone, address):
        """Добавление клиента
        :param user_id: id клиента
        :param name: имя клиента
        :param phone:  телефон клиента
        :param address:  адресс клиента
        :return:True если добавлен успешно"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("INSERT INTO Clients(id, name, phone, address, blacklisted) VALUES (?, ?, ?, ?, ?)",
                               [user_id, name, phone, address, 0])
                return cursor.rowcount == 1
        except sqlite3.Error as e:
            print(f"Ошибка при добавлении клиента: {e}")
            return False

    def delll(self, cl_id):
        with sqlite3.connect(self.db_file) as db:
            cursor = db.cursor()
            cursor.execute("DELETE FROM Clients WHERE id= ?", [cl_id])
            return cursor.rowcount > 0
###############################

    def block_client(self, client_id):
        """изменяет статус клиента blacklisted 0/1
        :param client_id: id клиента
        :return: True - выполнено, False - нет"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT blacklisted FROM Clients WHERE id = ?", [client_id])
                result = cursor.fetchone()
                if result is not None:
                    current_status = result[0]
                    new_status = 1 if current_status == 0 else 0
                    cursor.execute("UPDATE Clients SET blacklisted = ? WHERE id = ?", [new_status, client_id])
                    return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Не удалось заблокировать/разблокировать клиента: {e}")
            return False

    def orders_for_cleaner(self, cleaner_id):
        """возвращает список текущих заявок клинера
        :param cleaner_id: id клинера
        :return: Список заявок[(id, date_time), (id, date_time)]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT id, date_time FROM Orders WHERE status != ? AND staff_id = ?",
                               ['Уборка завершена', cleaner_id])
                cleaner_orders_all = [list(i) for i in cursor.fetchall()]
                result = []
                for i in cleaner_orders_all:
                    if i[1].split(', ')[0] == date.today().strftime('%d.%m.%Y'):
                        result.append(i)
                return False if len(result) == 0 else result
        except sqlite3.Error as e:
            print(f"Не удалось загрузить список текущих заявок клинера: {e}")
            return False

    def get_client_id(self, order_id):
        """возвращает id клиента
        :param order_id: id заказа
        :return: id (int)"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT client_id FROM Orders WHERE id = ?", [order_id])
                result = cursor.fetchone()
                return False if result is None else int(result[0])
        except sqlite3.Error as e:
            print(f"Не удалось получить id клиент: {e}")
            return False

    def get_order_data_for_cleaner(self, order_id):
        """возвращает id клиента
        :param order_id: id заказа
        :return: id клиента"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("""SELECT room_count, bathroom_count, fridge, stove, cabinets, dishes, microwave, 
                clothes, windows, balcony, price, order_time FROM Orders WHERE id = ?""", [order_id])
                result = cursor.fetchone()
                return False if result is None else result
        except sqlite3.Error as e:
            print(f"Не удалось загрузить данные по заказу: {e}")
            return False

    def change_order_status(self, order_id, status):
        """возвращает id клиента
        :param order_id: id заказа
        :param status: новый статус заявки
        :return: True - изменен, False - нет"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("UPDATE Orders SET status = ? WHERE id = ?", [status, order_id])
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Не удалось изменить статус заявки: {e}")
            return False

    def get_cleaner_reviews(self, cleaner_id):
        """:param cleaner_id: id клинера
        :return: список заявок с отзывами"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("""SELECT Orders.id, Orders.date_time 
                FROM Orders 
                JOIN Reviews ON Reviews.order_id = Orders.id
                WHERE Orders.staff_id = ?""", [cleaner_id])
                result = cursor.fetchall()
                return False if result is None else result
        except sqlite3.Error as e:
            print(f"Не удалось загрузить отзывы клинера: {e}")
            return False

    def get_cleaner_review_info(self, order_id):
        """:param order_id: id заявки
        :return: данные клиента, текст отзыва"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("""SELECT Clients.name, Clients.address, Reviews.review_text
                FROM Clients 
                JOIN Orders ON Orders.client_id = Clients.id
                JOIN Reviews ON Reviews.order_id = Orders.id
                WHERE Orders.id = ?""", [order_id])
                result = cursor.fetchone()
                return False if result is None else result
        except sqlite3.Error as e:
            print(f"Не удалось загрузить отзывы клинера: {e}")
            return False

    def get_cleaner_info(self, cleaner_id):
        """:param cleaner_id: id клинера
        :return: данные клинера (id, name, phone, hours_week, hours_day, work_schedule(1-доступен к работе, 2 - нет))"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("SELECT * FROM Staff WHERE id = ?", [cleaner_id])
                result = cursor.fetchone()
                return False if result is None else result
        except sqlite3.Error as e:
            print(f"Не удалось загрузить данные клинера: {e}")
            return False

    def change_cleaner_phone(self, cleaner_id, phone):
        """изменение номера телефона клинера
        :param cleaner_id: id клинера
        :param phone: новый телефон клинера
        :return: True - изменен, False - нет"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("UPDATE Staff SET contact_info = ? WHERE id = ?", [phone, cleaner_id])
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Не удалось изменить номер телефона клинера: {e}")
            return False
