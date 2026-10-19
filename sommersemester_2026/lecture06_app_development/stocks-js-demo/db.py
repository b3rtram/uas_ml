"""
db.py — DATABASE layer.

Stores the user's portfolio of tickers in SQLite. Nothing fancy:
one row per ticker, no duplicates, ordered by when they were added.

The DB is intentionally narrow — it persists *only* what needs to survive
restarts (the portfolio). The forecasts themselves are computed on demand
and not cached; that keeps the demo focused on the architecture, not on
cache invalidation.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

DB_FILE = Path(__file__).parent / "portfolio.db"


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolio (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker   TEXT    NOT NULL UNIQUE,
                added_at TEXT    NOT NULL
            )
            """
        )


init_db()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def add_to_portfolio(ticker: str) -> dict:
    """Add a ticker to the portfolio. Raises sqlite3.IntegrityError on duplicate."""
    ticker = ticker.upper().strip()
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO portfolio (ticker, added_at) VALUES (?, ?)",
            (ticker, _now_iso()),
        )
        row = conn.execute(
            "SELECT * FROM portfolio WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)


def list_portfolio() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM portfolio ORDER BY added_at ASC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_from_portfolio(stock_id: int) -> bool:
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM portfolio WHERE id = ?", (stock_id,))
        return cursor.rowcount > 0
