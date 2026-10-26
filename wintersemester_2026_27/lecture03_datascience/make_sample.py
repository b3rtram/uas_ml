"""Create sample/prices_sample.parquet: 10 % of all symbols from data/prices.parquet.

The sample keeps the raw, uncleaned rows, so the data-quality part of
Session03_Data_Stocks.ipynb works without the full 14 GB of JSON files.
Run the notebook once with the full data first (it creates data/prices.parquet).
"""

import numpy as np
import pandas as pd

FRACTION = 0.10
ALWAYS = ["AAPL", "NVDA", "TSLA", "BAYN.DE", "7203.T", "0700.HK", "NESN.SW", "MMEX"]   # used in the notebook

prices = pd.read_parquet("data/prices.parquet")
symbols = prices["symbol"].cat.categories.to_numpy()
rng = np.random.default_rng(42)
keep = set(rng.choice(symbols, int(len(symbols) * FRACTION), replace=False)) | set(ALWAYS)

sample = prices[prices["symbol"].isin(keep)].sort_values(["symbol", "date"])
sample["symbol"] = sample["symbol"].cat.remove_unused_categories()
sample.to_parquet("sample/prices_sample.parquet", compression="zstd", compression_level=19, index=False)
print(f"{sample['symbol'].nunique():,} symbols, {len(sample):,} rows")
