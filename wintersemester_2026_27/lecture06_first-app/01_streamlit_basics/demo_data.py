"""Made-up stock prices (random walk) so pages 1-9 work without internet and without an API key."""
import numpy as np
import pandas as pd

SYMBOLS = ["AAPL", "MSFT", "NVDA"]


def prices(days=120, seed=42):
    """One row per trading day: date, AAPL, MSFT, NVDA. Illustrative data, not real prices."""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(end="2026-11-13", periods=days)
    start = {"AAPL": 340.0, "MSFT": 500.0, "NVDA": 180.0}
    df = pd.DataFrame({"date": dates})
    for s in SYMBOLS:
        returns = rng.normal(0.0005, 0.015, days)          # about 1.5 % up or down per day
        df[s] = (start[s] * np.cumprod(1 + returns)).round(2)
    return df
