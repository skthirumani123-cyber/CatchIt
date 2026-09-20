"""
CatchIt: Smart Bus Schedule & Transportation Management System
Database Models, Schema Definition, and Seed Data Initialization
"""

import sqlite3
import os
import re
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'busflow.db')

DATABASE_BACKEND = os.environ.get('CATCHIT_DB', 'sqlite').strip().lower()
MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', '3306'))
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'catchit')

def using_mysql():
    return DATABASE_BACKEND == 'mysql'

def _mysql_connection(database=MYSQL_DATABASE):
    try:
        import mysql.connector
    except ImportError as exc:
        raise RuntimeError('Install mysql-connector-python or switch CATCHIT_DB back to sqlite.') from exc

    options = {
        'host': MYSQL_HOST,
        'port': MYSQL_PORT,
        'user': MYSQL_USER,
        'password': MYSQL_PASSWORD,
    }
    if database:
        options['database'] = database
    return _MySQLConnection(mysql.connector.connect(**options))

class _MySQLCursor:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, statement, params=None):
        statement = statement.replace('?', '%s')
        return self.cursor.execute(statement, params)

    def executemany(self, statement, params):
        return self.cursor.executemany(statement.replace('?', '%s'), params)

    def __getattr__(self, name):
        return getattr(self.cursor, name)

class _MySQLConnection:
    def __init__(self, connection):
        self.connection = connection

    def cursor(self):
        return _MySQLCursor(self.connection.cursor(dictionary=True))

    def __getattr__(self, name):
        return getattr(self.connection, name)

def _ensure_mysql_database():
    conn = _mysql_connection(database=None)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    conn.commit()
    cursor.close()
    conn.close()

class _MySQLSchemaCursor:
    """Translates the small SQLite DDL dialect used by the seed schema."""
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, statement, params=None):
        statement = re.sub(r'INTEGER PRIMARY KEY AUTOINCREMENT', 'INT PRIMARY KEY AUTO_INCREMENT', statement, flags=re.IGNORECASE)
        statement = re.sub(r'\bREAL\b', 'DOUBLE', statement, flags=re.IGNORECASE)
        statement = re.sub(r'\bTEXT\b', 'TEXT', statement, flags=re.IGNORECASE)
        return self.cursor.execute(statement, params)

    def __getattr__(self, name):
        return getattr(self.cursor, name)

def dict_factory(cursor, row):
    """Converts sqlite3 row tuples to dictionaries."""
    fields = [col[0] for col in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def get_db():
    """Returns a database connection with dictionary rows and foreign keys enabled."""
    if using_mysql():
        _ensure_mysql_database()
        return _mysql_connection()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = dict_factory
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initializes the database schema if tables do not exist."""
    conn = get_db()
    cursor = conn.cursor()
    if using_mysql():
        cursor = _MySQLSchemaCursor(cursor)

    # 1. Users table (Admin, Driver, Passenger)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'driver', 'passenger')),
        license_number TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Buses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS buses (
        bus_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bus_number TEXT UNIQUE NOT NULL,
        bus_type TEXT NOT NULL,
        capacity INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Maintenance', 'Out of Service'))
    );
    """)

    # 3. Routes table (with base fare)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS routes (
        route_id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_name TEXT NOT NULL,
        source TEXT NOT NULL,
        destination TEXT NOT NULL,
        distance_km INTEGER NOT NULL,
        base_fare REAL NOT NULL DEFAULT 80.0
    );
    """)

    # 4. Bus Stops table (with sequence & offset minutes from departure)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stops (
        stop_id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id INTEGER NOT NULL,
        stop_name TEXT NOT NULL,
        sequence INTEGER NOT NULL,
        offset_minutes INTEGER NOT NULL,
        latitude REAL,
        longitude REAL,
        FOREIGN KEY (route_id) REFERENCES routes(route_id) ON DELETE CASCADE
    );
    """)

    # 5. Schedules table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedules (
        schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        bus_id INTEGER NOT NULL,
        route_id INTEGER NOT NULL,
        driver_id INTEGER,
        departure_time TEXT NOT NULL,
        arrival_time TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'On Time' CHECK(status IN ('On Time', 'Delayed', 'Cancelled', 'Not Started')),
        occupancy TEXT NOT NULL DEFAULT 'Low' CHECK(occupancy IN ('Low', 'Medium', 'High', 'Full')),
        delay_minutes INTEGER NOT NULL DEFAULT 0,
        delay_reason TEXT,
        fare REAL NOT NULL DEFAULT 120.0,
        FOREIGN KEY (bus_id) REFERENCES buses(bus_id),
        FOREIGN KEY (route_id) REFERENCES routes(route_id),
        FOREIGN KEY (driver_id) REFERENCES users(id)
    );
    """)

    # 6. Delays audit log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS delays (
        delay_id INTEGER PRIMARY KEY AUTOINCREMENT,
        schedule_id INTEGER NOT NULL,
        delay_minutes INTEGER NOT NULL,
        reason TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id) ON DELETE CASCADE
    );
    """)

    # 7. Bookings table (with travel_date, seat_number, fare, verification status)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        schedule_id INTEGER NOT NULL,
        passenger_name TEXT NOT NULL,
        seat_number TEXT NOT NULL,
        travel_date TEXT NOT NULL,
        fare_paid REAL NOT NULL DEFAULT 120.0,
        booking_code TEXT UNIQUE NOT NULL,
        status TEXT NOT NULL DEFAULT 'Confirmed' CHECK(status IN ('Confirmed', 'Boarded', 'Cancelled', 'Completed')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id)
    );
    """)

    # 8. Driver Shifts table (track working hours)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS driver_shifts (
        shift_id INTEGER PRIMARY KEY AUTOINCREMENT,
        driver_id INTEGER NOT NULL,
        shift_date TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT,
        hours_worked REAL NOT NULL DEFAULT 0.0,
        status TEXT NOT NULL DEFAULT 'Active' CHECK(status IN ('Active', 'Completed')),
        FOREIGN KEY (driver_id) REFERENCES users(id)
    );
    """)

    conn.commit()
    cursor.close()
    conn.close()

def seed_data():
    """Populates realistic Karnataka transit data matching the design mockup and new features."""
    conn = get_db()
    cursor = conn.cursor()

    # Check if data already seeded
    cursor.execute("SELECT COUNT(*) AS count FROM users")
    if cursor.fetchone()['count'] > 0:
        conn.close()
        return

    print("Seeding CatchIt database with transit routes, drivers, and shifts...")

    # --- 1. USERS ---
    users_data = [
        # Admin
        ('Admin In-Charge', 'admin@busflow.com', '9845012345', generate_password_hash('admin123'), 'admin', None),
        # Primary Driver (matches Ravi Kumar)
        ('Ravi Kumar', 'driver@busflow.com', '9876543210', generate_password_hash('driver123'), 'driver', 'KA-123456'),
        # Primary Passenger (matches Skanda Bharadwaj)
        ('Skanda Bharadwaj', 'passenger@busflow.com', '9123456780', generate_password_hash('passenger123'), 'passenger', None),
        # Additional Drivers (Total 18 drivers)
        ('Manjunath Gowda', 'manju@busflow.com', '9880112233', generate_password_hash('driver123'), 'driver', 'KA-234567'),
        ('Suresh Nayak', 'suresh@busflow.com', '9880223344', generate_password_hash('driver123'), 'driver', 'KA-345678'),
        ('Venkatesh Rao', 'venky@busflow.com', '9880334455', generate_password_hash('driver123'), 'driver', 'KA-456789'),
        ('Anand Swamy', 'anand@busflow.com', '9880445566', generate_password_hash('driver123'), 'driver', 'KA-567890'),
        ('Praveen Kumar', 'praveen@busflow.com', '9880556677', generate_password_hash('driver123'), 'driver', 'KA-678901'),
        ('Basavaraj Patil', 'basava@busflow.com', '9880667788', generate_password_hash('driver123'), 'driver', 'KA-789012'),
        ('Raghavendra Bhat', 'raghu@busflow.com', '9880778899', generate_password_hash('driver123'), 'driver', 'KA-890123'),
        ('Channappa M', 'channa@busflow.com', '9880889900', generate_password_hash('driver123'), 'driver', 'KA-901234'),
        ('Girish Shetty', 'girish@busflow.com', '9880990011', generate_password_hash('driver123'), 'driver', 'KA-012345'),
        ('Shashidhar K', 'shashi@busflow.com', '9881001122', generate_password_hash('driver123'), 'driver', 'KA-112233'),
        ('Kiran Prasad', 'kiran@busflow.com', '9881112233', generate_password_hash('driver123'), 'driver', 'KA-223344'),
        ('Mahesh Hegde', 'mahesh@busflow.com', '9881223344', generate_password_hash('driver123'), 'driver', 'KA-334455'),
        ('Nagaraj Reddy', 'nagaraj@busflow.com', '9881334455', generate_password_hash('driver123'), 'driver', 'KA-445566'),
        ('Shivakumar B', 'shiva@busflow.com', '9881445566', generate_password_hash('driver123'), 'driver', 'KA-556677'),
        ('Ramesh Chandra', 'ramesh@busflow.com', '9881556677', generate_password_hash('driver123'), 'driver', 'KA-667788'),
        ('Vijay Kumar', 'vijay@busflow.com', '9881667788', generate_password_hash('driver123'), 'driver', 'KA-778899'),
        # Additional Passengers
        ('Ananya Sharma', 'ananya@example.com', '9900112233', generate_password_hash('user123'), 'passenger', None),
        ('Karthik Varma', 'karthik@example.com', '9900223344', generate_password_hash('user123'), 'passenger', None),
    ]

    cursor.executemany("""
    INSERT INTO users (name, email, phone, password_hash, role, license_number)
    VALUES (?, ?, ?, ?, ?, ?)
    """, users_data)

    # --- 2. BUSES (25 buses) ---
    buses_data = [
        ('KA01AB1234', 'AC Sleeper', 40, 'Active'),
        ('KA05CD5678', 'Non-AC', 45, 'Active'),
        ('KA09EF9012', 'Non-AC', 45, 'Active'),
        ('KA11GH3456', 'Volvo', 50, 'Maintenance'),
        ('KA13IJ7890', 'AC', 42, 'Active'),
        ('KA04KL2345', 'Volvo Multi-Axle', 48, 'Active'),
        ('KA06MN6789', 'AC Sleeper', 36, 'Active'),
        ('KA02OP1122', 'Non-AC Deluxe', 52, 'Active'),
        ('KA03QR3344', 'Electric AC', 45, 'Active'),
        ('KA07ST5566', 'Volvo', 50, 'Active'),
        ('KA08UV7788', 'AC Seater', 44, 'Active'),
        ('KA10WX9900', 'Non-AC', 55, 'Active'),
        ('KA12YZ1234', 'AC Sleeper', 40, 'Active'),
        ('KA14AA5678', 'Volvo', 52, 'Active'),
        ('KA15BB9012', 'Electric AC', 46, 'Active'),
        ('KA16CC3456', 'Non-AC Deluxe', 50, 'Active'),
        ('KA17DD7890', 'AC Sleeper', 38, 'Active'),
        ('KA18EE2345', 'Volvo Multi-Axle', 48, 'Active'),
        ('KA19FF6789', 'AC Seater', 42, 'Active'),
        ('KA20GG1122', 'Non-AC', 54, 'Active'),
        ('KA21HH3344', 'Volvo', 50, 'Active'),
        ('KA22II5566', 'Electric AC', 45, 'Active'),
        ('KA23JJ7788', 'AC Sleeper', 40, 'Active'),
        ('KA24KK9900', 'Non-AC', 52, 'Active'),
        ('KA25LL1234', 'Volvo', 50, 'Active'),
    ]

    cursor.executemany("""
    INSERT INTO buses (bus_number, bus_type, capacity, status)
    VALUES (?, ?, ?, ?)
    """, buses_data)

    # --- 3. ROUTES (12 routes with distance and base fares) ---
    routes_data = [
        ('Tumkur - Bangalore', 'Tumkur', 'Bangalore', 70, 120.0),
        ('Tumkur - Nagasandra', 'Tumkur', 'Nagasandra', 45, 80.0),
        ('Tumkur - Doddaballapur', 'Tumkur', 'Doddaballapur', 60, 95.0),
        ('Tumkur - Nelamangala', 'Tumkur', 'Nelamangala', 35, 60.0),
        ('Tumkur - Mysore', 'Tumkur', 'Mysore', 150, 220.0),
        ('Bangalore - Tumkur', 'Bangalore', 'Tumkur', 70, 120.0),
        ('Bangalore - Mysore', 'Bangalore', 'Mysore', 145, 210.0),
        ('Tumkur - Sira', 'Tumkur', 'Sira', 55, 85.0),
        ('Tumkur - Gubbi', 'Tumkur', 'Gubbi', 22, 40.0),
        ('Tumkur - Hassan', 'Tumkur', 'Hassan', 128, 190.0),
        ('Bangalore - Doddaballapur', 'Bangalore', 'Doddaballapur', 40, 70.0),
        ('Tumkur - Tiptur', 'Tumkur', 'Tiptur', 74, 110.0),
    ]

    cursor.executemany("""
    INSERT INTO routes (route_name, source, destination, distance_km, base_fare)
    VALUES (?, ?, ?, ?, ?)
    """, routes_data)

    # --- 4. STOPS ---
    stops_r1 = [
        (1, 'Tumkur KSRTC Bus Stand', 1, 0, 13.3409, 77.1010),
        (1, 'Kyathsandra Toll', 2, 15, 13.3157, 77.1592),
        (1, 'Dabaspet Junction', 3, 35, 13.2298, 77.2417),
        (1, 'Nelamangala Toll Gate', 4, 55, 13.0984, 77.3898),
        (1, 'Nagasandra Metro', 5, 65, 13.0475, 77.4988),
        (1, 'Yeshwanthpur TTMC', 6, 95, 13.0234, 77.5501),
        (1, 'Bangalore Majestic (KBS)', 7, 120, 12.9772, 77.5729),
    ]

    stops_r2 = [
        (2, 'Tumkur KSRTC Bus Stand', 1, 0, 13.3409, 77.1010),
        (2, 'Kyathsandra Toll', 2, 15, 13.3157, 77.1592),
        (2, 'Hirehalli Industrial Area', 3, 25, 13.2750, 77.1980),
        (2, 'Dabaspet Junction', 4, 38, 13.2298, 77.2417),
        (2, 'Nelamangala Bypass', 5, 55, 13.0984, 77.3898),
        (2, 'Nagasandra Metro Terminal', 6, 65, 13.0475, 77.4988),
    ]

    stops_r3 = [
        (3, 'Tumkur KSRTC Bus Stand', 1, 0, 13.3409, 77.1010),
        (3, 'Urdigere Cross', 2, 20, 13.3120, 77.2100),
        (3, 'Doddabelavangala', 3, 50, 13.2980, 77.4120),
        (3, 'Doddaballapur Bus Stand', 4, 75, 13.2925, 77.5432),
    ]

    stops_r4 = [
        (4, 'Tumkur KSRTC Bus Stand', 1, 0, 13.3409, 77.1010),
        (4, 'Kyathsandra', 2, 15, 13.3157, 77.1592),
        (4, 'Dabaspet', 3, 35, 13.2298, 77.2417),
        (4, 'Nelamangala TTMC', 4, 50, 13.0984, 77.3898),
    ]

    stops_r5 = [
        (5, 'Tumkur Bus Stand', 1, 0, 13.3409, 77.1010),
        (5, 'Kunigal Bypass', 2, 40, 13.0245, 77.0270),
        (5, 'Maddur Circle', 3, 110, 12.5840, 77.0450),
        (5, 'Mandya KSRTC Bus Stand', 4, 140, 12.5220, 76.8980),
        (5, 'Mysore KSRTC Suburb Stand', 5, 190, 12.3118, 76.6529),
    ]

    stops_r6 = [
        (6, 'Bangalore Majestic (KBS)', 1, 0, 12.9772, 77.5729),
        (6, 'Yeshwanthpur TTMC', 2, 25, 13.0234, 77.5501),
        (6, 'Nagasandra Metro', 3, 45, 13.0475, 77.4988),
        (6, 'Nelamangala Toll Gate', 4, 65, 13.0984, 77.3898),
        (6, 'Dabaspet Junction', 5, 85, 13.2298, 77.2417),
        (6, 'Kyathsandra Toll', 6, 105, 13.3157, 77.1592),
        (6, 'Tumkur KSRTC Bus Stand', 7, 120, 13.3409, 77.1010),
    ]

    all_stops = stops_r1 + stops_r2 + stops_r3 + stops_r4 + stops_r5 + stops_r6
    cursor.executemany("""
    INSERT INTO stops (route_id, stop_name, sequence, offset_minutes, latitude, longitude)
    VALUES (?, ?, ?, ?, ?, ?)
    """, all_stops)

    # --- 5. SCHEDULES (48 Schedules with fares) ---
    schedules_data = [
        (1, 1, 2, '08:00', '10:00', 'On Time', 'High', 0, None, 140.0),
        (2, 2, 4, '09:15', '10:20', 'Delayed', 'Medium', 15, 'Heavy traffic near Dabaspet toll', 85.0),
        (3, 3, 5, '10:30', '11:45', 'On Time', 'Low', 0, None, 95.0),
        (4, 4, 6, '11:45', '12:35', 'Cancelled', 'Low', 0, 'Technical maintenance', 60.0),
        (5, 5, 7, '07:30', '10:40', 'On Time', 'High', 0, None, 220.0),
        (1, 1, 2, '12:30', '14:30', 'Not Started', 'Low', 0, None, 140.0),
        (6, 6, 8, '08:30', '10:30', 'On Time', 'Full', 0, None, 160.0),
        (7, 2, 9, '09:45', '10:50', 'On Time', 'Medium', 0, None, 85.0),
        (8, 3, 10, '11:15', '12:30', 'Delayed', 'High', 20, 'Rain & slow moving traffic', 95.0),
        (9, 4, 11, '13:00', '13:50', 'On Time', 'Low', 0, None, 60.0),
        (10, 5, 12, '14:00', '17:10', 'On Time', 'Medium', 0, None, 220.0),
        (11, 1, 13, '15:30', '17:30', 'On Time', 'Full', 0, None, 140.0),
        (12, 6, 14, '16:15', '18:15', 'Delayed', 'Medium', 10, 'Signal delay at Yeshwanthpur', 160.0),
        (13, 2, 15, '17:00', '18:05', 'On Time', 'High', 0, None, 85.0),
        (14, 3, 16, '18:00', '19:15', 'On Time', 'Medium', 0, None, 95.0),
        (15, 7, 17, '06:00', '08:00', 'On Time', 'High', 0, None, 150.0),
        (16, 1, 18, '06:45', '08:45', 'On Time', 'Low', 0, None, 140.0),
        (17, 2, 19, '07:15', '08:20', 'On Time', 'Medium', 0, None, 85.0),
        (18, 5, 2, '08:45', '11:55', 'On Time', 'Full', 0, None, 220.0),
        (19, 1, 4, '09:30', '11:30', 'On Time', 'High', 0, None, 140.0),
        (20, 2, 5, '10:00', '11:05', 'On Time', 'Medium', 0, None, 85.0),
        (21, 3, 6, '10:45', '12:00', 'On Time', 'Low', 0, None, 95.0),
        (22, 4, 7, '12:15', '13:05', 'Not Started', 'Low', 0, None, 60.0),
        (23, 1, 8, '13:45', '15:45', 'On Time', 'High', 0, None, 140.0),
        (24, 6, 9, '14:30', '16:30', 'On Time', 'Medium', 0, None, 160.0),
        (25, 2, 10, '15:00', '16:05', 'On Time', 'High', 0, None, 85.0),
        (1, 1, 2, '16:30', '18:30', 'On Time', 'Full', 0, None, 140.0),
        (2, 2, 11, '17:30', '18:35', 'Delayed', 'Medium', 25, 'Bridge repair near Nelamangala', 85.0),
        (3, 3, 12, '18:30', '19:45', 'On Time', 'Low', 0, None, 95.0),
        (5, 4, 13, '19:00', '19:50', 'On Time', 'Medium', 0, None, 60.0),
        (6, 5, 14, '19:30', '22:40', 'On Time', 'High', 0, None, 220.0),
        (7, 1, 15, '20:15', '22:15', 'Not Started', 'Low', 0, None, 140.0),
        (8, 6, 16, '21:00', '23:00', 'On Time', 'Medium', 0, None, 160.0),
        (9, 2, 17, '05:30', '06:35', 'On Time', 'Low', 0, None, 85.0),
        (10, 3, 18, '06:30', '07:45', 'On Time', 'Medium', 0, None, 95.0),
        (11, 4, 19, '07:00', '07:50', 'On Time', 'Low', 0, None, 60.0),
        (12, 1, 2, '07:45', '09:45', 'On Time', 'High', 0, None, 140.0),
        (13, 6, 4, '08:15', '10:15', 'On Time', 'Full', 0, None, 160.0),
        (14, 2, 5, '08:45', '09:50', 'On Time', 'Medium', 0, None, 85.0),
        (15, 3, 6, '09:00', '10:15', 'On Time', 'Low', 0, None, 95.0),
        (16, 5, 7, '09:30', '12:40', 'On Time', 'High', 0, None, 220.0),
        (17, 1, 8, '10:15', '12:15', 'On Time', 'Medium', 0, None, 140.0),
        (18, 6, 9, '11:00', '13:00', 'On Time', 'High', 0, None, 160.0),
        (19, 2, 10, '11:30', '12:35', 'On Time', 'Low', 0, None, 85.0),
        (20, 3, 11, '12:00', '13:15', 'On Time', 'Medium', 0, None, 95.0),
        (21, 4, 12, '12:45', '13:35', 'On Time', 'Low', 0, None, 60.0),
        (22, 1, 13, '13:15', '15:15', 'On Time', 'High', 0, None, 140.0),
        (23, 6, 14, '14:15', '16:15', 'On Time', 'Medium', 0, None, 160.0),
    ]

    cursor.executemany("""
    INSERT INTO schedules (bus_id, route_id, driver_id, departure_time, arrival_time, status, occupancy, delay_minutes, delay_reason, fare)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, schedules_data)

    # --- 6. DELAYS AUDIT LOG ---
    delays_data = [
        (2, 15, 'Heavy traffic near Dabaspet toll'),
        (8, 20, 'Rain & slow moving traffic on NH48'),
        (12, 10, 'Signal delay at Yeshwanthpur flyover'),
        (27, 25, 'Bridge maintenance diversion near Nelamangala'),
    ]
    cursor.executemany("""
    INSERT INTO delays (schedule_id, delay_minutes, reason)
    VALUES (?, ?, ?)
    """, delays_data)

    # --- 7. SAMPLE BOOKINGS (Passenger Travel History) ---
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    last_week = (date.today() - timedelta(days=5)).isoformat()

    bookings_data = [
        # user_id, schedule_id, passenger_name, seat_number, travel_date, fare, booking_code, status
        (3, 1, 'Skanda Bharadwaj', '1A', today, 140.0, 'CI-2026-TKBLR-01', 'Confirmed'),
        (3, 3, 'Skanda Bharadwaj', '2D', today, 95.0, 'CI-2026-TKDBP-02', 'Confirmed'),
        (3, 1, 'Skanda Bharadwaj', '1D', yesterday, 140.0, 'CI-2026-TKBLR-99', 'Boarded'),
        (3, 5, 'Skanda Bharadwaj', '3A', last_week, 220.0, 'CI-2026-TKMYS-44', 'Completed'),
        (20, 1, 'Ananya Sharma', '2A', today, 140.0, 'CI-2026-TKBLR-03', 'Confirmed'),
        (21, 2, 'Karthik Varma', '4B', today, 85.0, 'CI-2026-TKNGS-04', 'Confirmed'),
    ]
    cursor.executemany("""
    INSERT INTO bookings (user_id, schedule_id, passenger_name, seat_number, travel_date, fare_paid, booking_code, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, bookings_data)

    # --- 8. DRIVER SHIFTS (Working Hours Tracking) ---
    shifts_data = [
        # driver_id, shift_date, start_time, end_time, hours_worked, status
        (2, today, '06:00', None, 6.5, 'Active'),  # Ravi Kumar active duty today
        (2, yesterday, '06:30', '14:30', 8.0, 'Completed'),
        (2, (date.today() - timedelta(days=2)).isoformat(), '07:00', '15:30', 8.5, 'Completed'),
        (2, (date.today() - timedelta(days=3)).isoformat(), '06:00', '14:00', 8.0, 'Completed'),
        (2, (date.today() - timedelta(days=4)).isoformat(), '07:30', '14:30', 7.0, 'Completed'),
        (4, today, '07:00', None, 5.5, 'Active'),
        (5, today, '08:00', None, 4.5, 'Active'),
    ]
    cursor.executemany("""
    INSERT INTO driver_shifts (driver_id, shift_date, start_time, end_time, hours_worked, status)
    VALUES (?, ?, ?, ?, ?, ?)
    """, shifts_data)

    conn.commit()
    conn.close()
    print("CatchIt database initialized and seeded successfully!")

def reset_and_seed():
    """Drops and recreates all tables for clean schema updates."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
    seed_data()

if __name__ == '__main__':
    reset_and_seed()
