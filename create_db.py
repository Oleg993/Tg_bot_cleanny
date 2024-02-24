# import sqlite3
# from database import DataBase as DB
#
# with sqlite3.connect('cleanny.db') as db:
#     cursor = db.cursor()
#
#     query = """
#     CREATE TABLE IF NOT EXISTS Staff (
#         id INTEGER,
#         name TEXT,
#         contact_info TEXT,
#         worked_hours_current_week REAL,
#         worked_hours_day REAL,
#         work_schedule TEXT
#     );
#
#     CREATE TABLE IF NOT EXISTS Orders (
#         id INTEGER PRIMARY KEY,
#         order_date TEXT,
#         status TEXT,
#         date_time TEXT,
#         address TEXT,
#         client_id INTEGER,
#         staff_id INTEGER,
#         room_count INTEGER,
#         bathroom_count INTEGER,
#         fridge INTEGER,
#         stove INTEGER,
#         cabinets INTEGER,
#         dishes INTEGER,
#         microwave INTEGER,
#         clothes INTEGER,
#         windows INTEGER,
#         balcony INTEGER,
#         discount REAL,
#         price TEXT,
#         order_time REAL,
#         FOREIGN KEY (client_id) REFERENCES clients(id),
#         FOREIGN KEY (staff_id) REFERENCES staff(id)
#     );
#
#     CREATE TABLE IF NOT EXISTS Clients (
#         id INTEGER,
#         name TEXT,
#         phone TEXT,
#         address TEXT,
#         blacklisted INTEGER DEFAULT 0
#     );
#
#     CREATE TABLE IF NOT EXISTS Reviews (
#         id INTEGER PRIMARY KEY,
#         review_text TEXT,
#         date TEXT,
#         order_id INTEGER,
#         FOREIGN KEY (order_id) REFERENCES orders(id)
#     );
#
#     CREATE TABLE IF NOT EXISTS Complaints (
#         id INTEGER PRIMARY KEY,
#         complaint_text TEXT,
#         date TEXT,
#         order_id INTEGER,
#         FOREIGN KEY (order_id) REFERENCES orders(id)
#     );
#
#      CREATE TABLE IF NOT EXISTS equipment_distribution (
#         id INTEGER PRIMARY KEY,
#         material_name INTEGER,
#         staff_id INTEGER,
#         order_id INTEGER,
#         date_received TEXT,
#         date_returned TEXT,
#         FOREIGN KEY (material_name) REFERENCES materials(id),
#         FOREIGN KEY (staff_id) REFERENCES staff(id),
#         FOREIGN KEY (order_id) REFERENCES orders(id)
#     );
#
#     CREATE TABLE IF NOT EXISTS materials (
#         id INTEGER PRIMARY KEY,
#         date_came TEXT,
#         unit_measure TEXT,
#         valid_until TEXT,
#         quantity REAL,
#         material_name TEXT
#     );
#
#         CREATE TABLE IF NOT EXISTS daily_statistics (
#         id INTEGER PRIMARY KEY,
#         date TEXT,
#         staff_id INTEGER,
#         broken_equipment_count INTEGER,
#         earned_money REAL,
#         order_count INTEGER,
#         worked_hours REAL,
#         bot_visits INTEGER,
#         FOREIGN KEY (staff_id) REFERENCES staff(id)
#     );
#
#         CREATE TABLE IF NOT EXISTS monthly_statistics (
#         id INTEGER PRIMARY KEY,
#         month TEXT,
#         staff_id INTEGER,
#         broken_equipment_count INTEGER,
#         earned_money REAL,
#         order_count INTEGER,
#         worked_hours REAL,
#         bot_visits INTEGER,
#         FOREIGN KEY (staff_id) REFERENCES staff(id)
#     );
#
#         CREATE TABLE IF NOT EXISTS Admins (
#         id INTEGER,
#         name TEXT,
#         phone TEXT
#     );
#
#         CREATE TABLE IF NOT EXISTS Social_media (
#         id INTEGER PRIMARY KEY,
#         name TEXT,
#         link TEXT,
#         messanger_or_link INTEGER DEFAULT 0
#     );
#
#     """
#     cursor.executescript(query)
#
#
# DB().add_admin(1924589846, 'Олег', '+37529 821 89 14')
# DB().add_cleaner(6638258539, 'Иван Иванович', "+37529 937 99 92", 0, 0, 1)
# DB().add_cleaner(111, 'Долматов Алексей', "+37529 171 83 54", 18, 0, 1)
# DB().add_cleaner(222, 'Вакуленко Василий', "+37533 374 32 97", 22, 0, 1)
# DB().add_cleaner(333, 'Киркоров Филипп', "+37544 876 83 23", 24, 0, 1)
# DB().add_cleaner(444, 'Михайлов Станислав', "+37529 573 11 35", 17, 0, 1)
# DB().add_cleaner(555, 'Лепс Григорий', "+37529 221 37 90", 5, 0, 1)
#
# DB().add_client(28358273, 'Джон Буш Сергеевич', "+37529 123 34 64", 'г. Вашингтон, ул. Центральная, д. 1')
# DB().add_client(834756873456, 'Байден Джон Семенович', "+37529 345 87 12", 'г. Нью Джерси, пр-т Пушкинский, д. 78')
# DB().add_client(92384234, 'Трамп Дональд Макдакович', "+37533 981 01 62", 'г. Детройт, б-р Независимости, д. 15')
# DB().add_client(2345236574892, 'Обама Барак Викторович', "+37544 758 12 19", 'г. Нью Йорк, ул. Привокзальная, д. 26')
#
#
# print('ready')
