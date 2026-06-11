# vehicle_database.py

import sqlite3
import os
from datetime import datetime

DB_PATH = "data/surveillance.db"


def init_vehicle_db():
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate_number TEXT UNIQUE,
            owner_name TEXT,
            vehicle_type TEXT,
            department TEXT,
            status TEXT,
            remarks TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            camera_source TEXT,
            plate_number TEXT,
            owner_name TEXT,
            vehicle_type TEXT,
            department TEXT,
            status TEXT,
            snapshot_path TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_vehicle_record(plate_number, owner_name, vehicle_type, department, status, remarks):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    plate_number = plate_number.upper().replace(" ", "")

    cursor.execute("""
        INSERT OR REPLACE INTO vehicle_watchlist
        (plate_number, owner_name, vehicle_type, department, status, remarks)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        plate_number,
        owner_name,
        vehicle_type,
        department,
        status,
        remarks
    ))

    conn.commit()
    conn.close()


def get_vehicle_record(plate_number):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    plate_number = plate_number.upper().replace(" ", "")

    cursor.execute("""
        SELECT plate_number, owner_name, vehicle_type, department, status, remarks
        FROM vehicle_watchlist
        WHERE plate_number = ?
    """, (plate_number,))

    row = cursor.fetchone()
    conn.close()

    return row


def insert_vehicle_log(camera_source, plate_number, owner_name, vehicle_type, department, status, snapshot_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO vehicle_logs
        (timestamp, camera_source, plate_number, owner_name, vehicle_type, department, status, snapshot_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        camera_source,
        plate_number,
        owner_name,
        vehicle_type,
        department,
        status,
        snapshot_path
    ))

    conn.commit()
    conn.close()


def fetch_vehicle_records():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, plate_number, owner_name, vehicle_type, department, status, remarks
        FROM vehicle_watchlist
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def fetch_vehicle_logs(limit=100):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, timestamp, camera_source, plate_number, owner_name, vehicle_type, department, status, snapshot_path
        FROM vehicle_logs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return rows