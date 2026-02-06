import sqlite3
import logging

logger = logging.getLogger("theta.db")
DB_FILE = "teramind.db"


def _conn():
    return sqlite3.connect(DB_FILE)


def init_db():
    with _conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS stats (key TEXT PRIMARY KEY, value INTEGER)")
        c.execute("INSERT OR IGNORE INTO stats (key, value) VALUES ('posts_analyzed', 0)")
        c.execute("INSERT OR IGNORE INTO stats (key, value) VALUES ('dms_answered', 0)")
    logger.info("Database initialized")


def increment_posts_analyzed():
    with _conn() as c:
        c.execute("UPDATE stats SET value = value + 1 WHERE key = 'posts_analyzed'")


def increment_dms_answered():
    with _conn() as c:
        c.execute("UPDATE stats SET value = value + 1 WHERE key = 'dms_answered'")


def get_stats() -> dict:
    with _conn() as c:
        rows = c.execute("SELECT key, value FROM stats").fetchall()
    return {k: v for k, v in rows} if rows else {}
