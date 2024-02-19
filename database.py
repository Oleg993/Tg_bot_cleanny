import sqlite3
import datetime
import telebot

bot = telebot.TeleBot('6748980136:AAEh6eAhemwrxa-oehIo0JzzWsfoF250pxg')


class DataBase:
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
                return result[0] == '1' if result is not None else False
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
                return result[0] == '1' if result is not None else False
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
                query = ("""SELECT id FROM Orders 
                           WHERE client_id = ?""")
                cursor.execute(query, [client_id])
                result = cursor.fetchall()
                return False if len(result) == 0 else [i[0] for i in result]
        except sqlite3.Error as e:
            print(f"Не удалось загрузить список товаров категории: {e}")
            return False

    def get_order(self, order_id):
        """возвращает данные по заказу
        :param order_id: id клиента
        :return: список данных заказа [id, дата, имя Клинера, кол-во комнат, кол-во уборных, доп.услуги, цена]"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                query = ("""SELECT Orders.id, Orders.order_date, Staff.name, 
                Staff.room_count, Staff.bathroom_count, Staff.other_details, Orders.price 
                FROM Orders 
                JOIN Staff ON Staff.id = Orders.staff_id
                WHERE order_id = ?""")
                cursor.execute(query, [order_id])
                result = cursor.fetchall()
                return False if len(result) == 0 else [i[0] for i in result]
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
        other_details]
        :return: True - добавлено, False - нет"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("""INSERT INTO Orders (order_date, status, address, client_id, staff_id, discount, 
                room_count, bathroom_count, other_details) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", [*data])
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
                cursor.execute("SELECT id, name, contact_info, address FROM Clients WHERE id= ?", [client_id])
                data = cursor.fetchone()
                return data if len(data) != 0 else False
        except sqlite3.Error as e:
            print(f"Не удалось получить данные клиента: {e}")
            return False

    def correct_client_data(self, client_data, client_id):
        """изменение данных клиента
        :param client_data: [name, phone, address]
        :param client_id: id клиента
        :return:True если изменения внесены успешно иначе False"""
        try:
            with sqlite3.connect(self.db_file) as db:
                cursor = db.cursor()
                cursor.execute("""UPDATE Clients SET name = ?, phone = ?, address = ? WHERE id = ?""",
                               [*client_data, client_id])
                return cursor.rowcount == 1
        except sqlite3.Error as e:
            print(f"Ошибка при изменении данных: {e}")
            return False
































