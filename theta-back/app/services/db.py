# backend/app/services/db.py
import sqlite3

DB_FILE = "teramind.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stats (key TEXT PRIMARY KEY, value INTEGER)''')
    c.execute('''INSERT OR IGNORE INTO stats (key, value) VALUES ('posts_analyzed', 0)''')
    conn.commit()
    conn.close()

def increment_posts_analyzed():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE stats SET value = value + 1 WHERE key = 'posts_analyzed'")
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("SELECT value FROM stats WHERE key = 'posts_analyzed'")
        result = c.fetchone()
        count = result[0] if result else 0
    except:
        count = 0
    conn.close()
    return count