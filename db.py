# db.py
import sqlite3
from datetime import datetime

DB_PATH = "prices.db"

def init_db(path=DB_PATH):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        url TEXT UNIQUE,
        title TEXT,
        created_at TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS prices (
        id INTEGER PRIMARY KEY,
        product_id INTEGER,
        price REAL,
        ts TEXT,
        FOREIGN KEY(product_id) REFERENCES products(id)
    )
    """)
    conn.commit()
    conn.close()

def add_product(url, title=None, path=DB_PATH):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    try:
        c.execute("INSERT INTO products (url, title, created_at) VALUES (?, ?, ?)", (url, title, now))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    row = c.execute("SELECT id, url, title FROM products WHERE url = ?", (url,)).fetchone()
    conn.close()
    if row:
        return {"id": row[0], "url": row[1], "title": row[2]}
    return None

def add_price(product_id, price, ts=None, path=DB_PATH):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    ts = ts or datetime.utcnow().isoformat()
    c.execute("INSERT INTO prices (product_id, price, ts) VALUES (?, ?, ?)", (product_id, price, ts))
    conn.commit()
    conn.close()

def list_products(path=DB_PATH):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    rows = c.execute("SELECT id, url, title FROM products").fetchall()
    conn.close()
    return [{"id": r[0], "url": r[1], "title": r[2]} for r in rows]

def get_price_history(product_id, path=DB_PATH):
    conn = sqlite3.connect(path)
    c = conn.cursor()
    rows = c.execute("SELECT price, ts FROM prices WHERE product_id=? ORDER BY ts", (product_id,)).fetchall()
    conn.close()
    return [{"price": r[0], "ts": r[1]} for r in rows]
