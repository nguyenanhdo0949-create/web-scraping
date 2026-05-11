import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH
from logger import get_logger

logger = get_logger("database")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def create_db():
    """Create tables: books, quotes + unified view."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT    NOT NULL,
            price        TEXT    DEFAULT '',
            rating       INTEGER DEFAULT 0,
            availability TEXT    DEFAULT '',
            scraped_by   TEXT    DEFAULT 'playwright',
            created_at   DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            text       TEXT    NOT NULL,
            author     TEXT    DEFAULT '',
            tags       TEXT    DEFAULT '',
            scraped_by TEXT    DEFAULT 'selenium',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Unified view for the dashboard
    c.execute("DROP VIEW IF EXISTS all_data")
    c.execute("""
        CREATE VIEW all_data AS
        SELECT id,
               title              AS title,
               price              AS secondary,
               rating,
               availability       AS extra,
               'books'            AS data_type,
               scraped_by,
               created_at
        FROM books
        UNION ALL
        SELECT id,
               text               AS title,
               author             AS secondary,
               0                  AS rating,
               tags               AS extra,
               'quotes'           AS data_type,
               scraped_by,
               created_at
        FROM quotes
    """)

    conn.commit()
    conn.close()
    logger.info(f"Database ready → {DB_PATH}")


# ─── INSERT ──────────────────────────────────────────────────────────────────

def insert_books(data: list):
    if not data:
        logger.warning("insert_books: empty list, skipping")
        return
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM books")
    c.executemany("""
        INSERT INTO books (title, price, rating, availability, scraped_by)
        VALUES (:title, :price, :rating, :availability, :scraped_by)
    """, data)
    conn.commit()
    conn.close()
    logger.info(f"Inserted {len(data)} books")


def insert_quotes(data: list):
    if not data:
        logger.warning("insert_quotes: empty list, skipping")
        return
    conn = get_db_connection()
    c = conn.cursor()
    # Xóa cũ theo scraped_by để tránh duplicate
    scraped_by_val = data[0].get("scraped_by", "selenium")
    c.execute("DELETE FROM quotes WHERE scraped_by = ?", (scraped_by_val,))
    c.executemany("""
        INSERT INTO quotes (text, author, tags, scraped_by)
        VALUES (:text, :author, :tags, :scraped_by)
    """, data)
    conn.commit()
    conn.close()
    logger.info(f"Inserted {len(data)} quotes (scraped_by={scraped_by_val})")


def insert_quotes_append(data: list):
    """Used by Scrapy pipeline — appends instead of replacing."""
    if not data:
        return
    conn = get_db_connection()
    c = conn.cursor()
    c.executemany("""
        INSERT INTO quotes (text, author, tags, scraped_by)
        VALUES (:text, :author, :tags, :scraped_by)
    """, data)
    conn.commit()
    conn.close()


# ─── QUERY ──────────────────────────────────────────────────────────────────

def query_unified(keyword=None, data_type=None, scraped_by=None, limit=None, offset=0):
    conn = get_db_connection()
    c = conn.cursor()
    q = "SELECT * FROM all_data WHERE 1=1"
    params = []
    if keyword:
        q += " AND (title LIKE ? OR secondary LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if data_type:
        q += " AND data_type = ?"
        params.append(data_type)
    if scraped_by:
        q += " AND scraped_by = ?"
        params.append(scraped_by)
    q += " ORDER BY data_type, created_at DESC"
    if limit:
        q += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
    c.execute(q, params)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def count_unified(keyword=None, data_type=None, scraped_by=None):
    conn = get_db_connection()
    c = conn.cursor()
    q = "SELECT COUNT(*) FROM all_data WHERE 1=1"
    params = []
    if keyword:
        q += " AND (title LIKE ? OR secondary LIKE ?)"
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if data_type:
        q += " AND data_type = ?"
        params.append(data_type)
    if scraped_by:
        q += " AND scraped_by = ?"
        params.append(scraped_by)
    c.execute(q, params)
    count = c.fetchone()[0]
    conn.close()
    return count


def get_stats():
    conn = get_db_connection()
    c = conn.cursor()
    stats = {}

    c.execute("SELECT COUNT(*) FROM books")
    stats["books_total"] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM quotes WHERE scraped_by='selenium'")
    stats["quotes_selenium"] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM quotes WHERE scraped_by='scrapy'")
    stats["quotes_scrapy"] = c.fetchone()[0]

    stats["quotes_total"] = stats["quotes_selenium"] + stats["quotes_scrapy"]

    c.execute("SELECT COUNT(*) FROM all_data")
    stats["total"] = c.fetchone()[0]

    c.execute("SELECT MAX(created_at) FROM books")
    row = c.fetchone()[0]
    stats["last_updated"] = row if row else "Never"

    conn.close()
    return stats