"""DATA LAYER: everything that reads or writes data (FMP API, SQLite).
Knows nothing about HTTP and nothing about the model."""
import os
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))          # FMP_API_KEY comes from the .env file, never from the code
FMP_URL = "https://financialmodelingprep.com/stable/historical-price-eod/light"
DB_PATH = Path(__file__).parent / "stock.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS prices (
    symbol TEXT NOT NULL,
    date   TEXT NOT NULL,
    close  REAL NOT NULL,
    PRIMARY KEY (symbol, date)                 -- one row per symbol and day, no duplicates
);
CREATE TABLE IF NOT EXISTS predictions (
    symbol     TEXT NOT NULL,
    as_of      TEXT NOT NULL,                  -- last known day
    close      REAL NOT NULL,
    return_pct REAL NOT NULL,                  -- predicted return for the next day, in %
    close_next REAL NOT NULL,                  -- predicted price for the next day
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (symbol, as_of)
);
"""


# ---- external data: the FMP API
def fetch_prices(symbol, days=60):
    """[{'date': '2026-11-06', 'close': 342.37}, ...], oldest first. Empty list = unknown symbol."""
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        raise RuntimeError("FMP_API_KEY missing: put FMP_API_KEY=... into the .env file")
    start = (date.today() - timedelta(days=days)).isoformat()
    r = requests.get(FMP_URL, params={"symbol": symbol, "from": start, "apikey": api_key}, timeout=10)
    r.raise_for_status()
    return [{"date": row["date"], "close": row["price"]} for row in reversed(r.json())]


# ---- stored data: SQLite
def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row              # rows behave like dicts: row["close"]
    con.executescript(SCHEMA)                  # create the tables on first use
    return con


def save_prices(symbol, prices):
    con = connect()
    with con:                                  # with = commit at the end
        con.executemany("""INSERT INTO prices (symbol, date, close) VALUES (?, ?, ?)
                           ON CONFLICT (symbol, date) DO UPDATE SET close = excluded.close""",
                        [(symbol, p["date"], p["close"]) for p in prices])
    con.close()


def save_prediction(p):
    con = connect()
    with con:
        con.execute("""INSERT INTO predictions (symbol, as_of, close, return_pct, close_next)
                       VALUES (:symbol, :as_of, :close, :return_pct, :close_next)
                       ON CONFLICT (symbol, as_of) DO UPDATE SET
                           return_pct = excluded.return_pct, close_next = excluded.close_next,
                           created_at = datetime('now')""", p)
    con.close()


def get_predictions(symbol, n=10):
    con = connect()
    rows = con.execute("SELECT * FROM predictions WHERE symbol = ? ORDER BY as_of DESC LIMIT ?", (symbol, n)).fetchall()
    con.close()
    return [dict(r) for r in rows]
