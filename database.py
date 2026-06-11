# database.py

import sqlite3
from datetime import datetime
import os

DB_PATH = "data/surveillance.db"


def init_db():
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detection_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            camera_source TEXT,
            detected_object TEXT,
            confidence REAL,
            threat_level TEXT,
            snapshot_path TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_log(camera_source, detected_object, confidence, threat_level, snapshot_path=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO detection_logs 
        (timestamp, camera_source, detected_object, confidence, threat_level, snapshot_path)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        camera_source,
        detected_object,
        round(float(confidence), 2),
        threat_level,
        snapshot_path
    ))

    conn.commit()
    conn.close()


def fetch_logs(limit=100):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, timestamp, camera_source, detected_object, confidence, threat_level, snapshot_path
        FROM detection_logs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def count_by_threat():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT threat_level, COUNT(*)
        FROM detection_logs
        GROUP BY threat_level
    """)

    rows = cursor.fetchall()
    conn.close()

    return dict(rows)