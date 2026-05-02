import sqlite3

def create_db():
    conn = sqlite3.connect("database/products.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price TEXT,
            source TEXT
        )
    """)

    conn.commit()
    conn.close()


def insert_data(data):
    conn = sqlite3.connect("database/products.db")
    cursor = conn.cursor()

    # reset dữ liệu
    cursor.execute("DELETE FROM products")

    for item in data:
        cursor.execute("""
            INSERT INTO products (title, price, source)
            VALUES (?, ?, ?)
        """, (item["title"], item["price"], item["source"]))

    conn.commit()
    conn.close()