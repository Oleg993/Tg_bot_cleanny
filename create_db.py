import sqlite3

with sqlite3.connect('cleanny.db') as db:
    cursor = db.cursor()

    query = """
    CREATE TABLE IF NOT EXISTS Staff (
        id INTEGER,
        name TEXT,
        contact_info TEXT,
        worked_hours_current_week REAL,
        work_schedule TEXT
    );

    CREATE TABLE IF NOT EXISTS Orders (
        id INTEGER PRIMARY KEY,
        order_date TEXT,
        status TEXT,
        date_time TEXT,
        address TEXT,
        client_id INTEGER,
        staff_id INTEGER,
        room_count INTEGER,
        bathroom_count INTEGER,
        fridge INTEGER,
        stove INTEGER,
        cabinets INTEGER,
        dishes INTEGER,
        microwave INTEGER,
        clothes INTEGER,
        windows INTEGER,
        balcony INTEGER,
        discount REAL,
        price TEXT,
        order_time REAL,
        FOREIGN KEY (client_id) REFERENCES clients(id),
        FOREIGN KEY (staff_id) REFERENCES staff(id)
    );

    CREATE TABLE IF NOT EXISTS Clients (
        id INTEGER,
        name TEXT,
        phone TEXT,
        address TEXT,
        blacklisted INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS Reviews (
        id INTEGER PRIMARY KEY,
        review_text TEXT,
        date TEXT,
        order_id INTEGER,
        FOREIGN KEY (order_id) REFERENCES orders(id)
    );

    CREATE TABLE IF NOT EXISTS Complaints (
        id INTEGER PRIMARY KEY,
        complaint_text TEXT,
        date TEXT,
        order_id INTEGER,
        FOREIGN KEY (order_id) REFERENCES orders(id)
    );

     CREATE TABLE IF NOT EXISTS equipment_distribution (
        id INTEGER PRIMARY KEY,
        material_name INTEGER,
        staff_id INTEGER,
        order_id INTEGER,
        date_received TEXT,
        date_returned TEXT,
        FOREIGN KEY (material_name) REFERENCES materials(id),
        FOREIGN KEY (staff_id) REFERENCES staff(id),
        FOREIGN KEY (order_id) REFERENCES orders(id)
    );

    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY,
        date_came TEXT,
        unit_measure TEXT,
        valid_until TEXT,
        quantity REAL,
        material_name TEXT
    );

        CREATE TABLE IF NOT EXISTS daily_statistics (
        id INTEGER PRIMARY KEY,
        date TEXT,
        staff_id INTEGER,
        broken_equipment_count INTEGER,
        earned_money REAL,
        order_count INTEGER,
        worked_hours REAL,
        bot_visits INTEGER,
        FOREIGN KEY (staff_id) REFERENCES staff(id)
    );

        CREATE TABLE IF NOT EXISTS monthly_statistics (
        id INTEGER PRIMARY KEY,
        month TEXT,
        staff_id INTEGER,
        broken_equipment_count INTEGER,
        earned_money REAL,
        order_count INTEGER,
        worked_hours REAL,
        bot_visits INTEGER,
        FOREIGN KEY (staff_id) REFERENCES staff(id)
    );

        CREATE TABLE IF NOT EXISTS Admins (
        id INTEGER,
        name TEXT,
        phone TEXT
    );

        CREATE TABLE IF NOT EXISTS Social_media (
        id INTEGER PRIMARY KEY,
        name TEXT,
        link TEXT,
        messanger_or_link INTEGER DEFAULT 0
    );

    """
    cursor.executescript(query)


print('ready')
