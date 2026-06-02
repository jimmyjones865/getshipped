import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = "/data/labels.db"


def init_db():
    with _conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS labels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                recipient_name TEXT,
                recipient_zip TEXT,
                recipient_city TEXT,
                recipient_country TEXT,
                product_code TEXT,
                product_name TEXT,
                weight_g INTEGER,
                tracking_number TEXT,
                ref_no TEXT
            )
        """)
        # Migration: add recipient_zip if table existed before this column was added
        try:
            conn.execute("ALTER TABLE labels ADD COLUMN recipient_zip TEXT")
        except Exception:
            pass


@contextmanager
def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def log_label(recipient_name: str, recipient_zip: str, recipient_city: str,
              recipient_country: str, product_code: str, product_name: str,
              weight_g: int, tracking_number: str, ref_no: str):
    with _conn() as conn:
        conn.execute(
            """INSERT INTO labels
               (created_at, recipient_name, recipient_zip, recipient_city, recipient_country,
                product_code, product_name, weight_g, tracking_number, ref_no)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                datetime.now(timezone.utc).isoformat(),
                recipient_name, recipient_zip, recipient_city, recipient_country,
                product_code, product_name, weight_g,
                tracking_number, ref_no,
            ),
        )


def get_labels(limit: int = 50) -> list[dict]:
    with _conn() as conn:
        rows = conn.execute(
            "SELECT * FROM labels ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]
