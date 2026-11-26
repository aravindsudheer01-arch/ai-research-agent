"""Atomic, shared SQLite request budget for a single demo deployment."""
import sqlite3
import time
from pathlib import Path


def reserve_request(path='outputs/demo_usage.sqlite3', *, now=None):
    now = time.time() if now is None else now
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path, timeout=5) as db:
        db.execute('CREATE TABLE IF NOT EXISTS requests (created REAL NOT NULL)')
        db.execute('BEGIN IMMEDIATE')
        db.execute('DELETE FROM requests WHERE created <= ?', (now - 86400,))
        daily, minute = db.execute(
            'SELECT COUNT(*), COALESCE(SUM(created > ?), 0) FROM requests', (now - 60,)
        ).fetchone()
        if daily >= 20 or minute >= 1:
            return False
        db.execute('INSERT INTO requests VALUES (?)', (now,))
    return True
