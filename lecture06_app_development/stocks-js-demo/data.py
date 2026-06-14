"""
data.py — DATA ACQUISITION layer.

Wraps yfinance so the rest of the code doesn't import it directly.
If Yahoo changes their API again (they do, periodically), only this
file needs to change.
"""

from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf


def fetch_stock_history(ticker: str, days: int = 365) -> pd.DataFrame:
    """
    Fetch the last `days` of daily closing prices for `ticker`.

    Returns a DataFrame with two columns:
        ds  — pandas datetime (the date)
        y   — float (the closing price)

    These column names are what Prophet expects — that lets forecast.py
    use the DataFrame directly without any renaming.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    df = yf.download(
        ticker,
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        progress=False,
        auto_adjust=True,
    )

    if df.empty:
        raise ValueError(
            f"No data returned for ticker '{ticker}'. "
            f"Try symbols like AAPL, MSFT, TSLA, SAP.DE."
        )

    # In recent yfinance versions, a single-ticker download returns a
    # MultiIndex on the columns. squeeze() flattens "Close" to a plain Series.
    close_prices = df["Close"].squeeze()

    return pd.DataFrame({
        "ds": pd.to_datetime(close_prices.index).tz_localize(None),
        "y": close_prices.values.astype(float),
    }).reset_index(drop=True)
