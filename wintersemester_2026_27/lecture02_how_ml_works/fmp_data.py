"""Download daily stock prices from Financial Modeling Prep (FMP).

The API key is read from the environment variable FMP_API_KEY
(or from a .env file anywhere above this folder).

The raw API response (JSON) is cached in ./data/, so the API is only
called once per ticker. Delete the JSON file to force a fresh download.
"""

import json
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import find_dotenv, load_dotenv

BASE_URL = "https://financialmodelingprep.com/stable/historical-price-eod/full"
DATA_DIR = Path(__file__).parent / "data"


def fetch_raw(symbol: str, start: str = "2015-01-01", refresh: bool = False) -> list[dict]:
    """Return the raw FMP response: a list of JSON objects, one per trading day (newest first)."""
    cache = DATA_DIR / f"{symbol}.json"

    if cache.exists() and not refresh:
        rows = json.loads(cache.read_text())
        print(f"Loaded {len(rows)} days for {symbol} from cache ({cache.name})")
        return rows

    load_dotenv(find_dotenv(usecwd=True))
    api_key = os.getenv("FMP_API_KEY")
    if not api_key:
        raise RuntimeError(
            "FMP_API_KEY not set. Get a free key at https://financialmodelingprep.com "
            "and put FMP_API_KEY=... into a .env file."
        )

    response = requests.get(
        BASE_URL,
        params={"symbol": symbol, "from": start, "apikey": api_key},
        timeout=30,
    )
    response.raise_for_status()
    rows = response.json()
    if not isinstance(rows, list) or not rows:
        raise RuntimeError(f"FMP returned no data for {symbol}: {str(rows)[:200]}")

    DATA_DIR.mkdir(exist_ok=True)
    cache.write_text(json.dumps(rows, indent=2))
    print(f"Downloaded {len(rows)} days for {symbol} from FMP -> {cache.name}")
    return rows


def load_prices(symbol: str, start: str = "2015-01-01", refresh: bool = False) -> pd.DataFrame:
    """Return daily OHLCV prices for `symbol` as a DataFrame, oldest day first, indexed by date."""
    df = pd.DataFrame(fetch_raw(symbol, start, refresh))
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()  # FMP delivers newest first
    return df[["open", "high", "low", "close", "volume"]]


if __name__ == "__main__":
    print(load_prices("AAPL", refresh=True).tail())
