"""BUSINESS LAYER: what the app actually does: prices -> features -> model -> prediction.
Knows nothing about HTTP and writes no SQL. It asks the data layer for data."""
import functools
from pathlib import Path

import joblib
import pandas as pd

import data

MODEL_PATH = Path(__file__).parent / "models" / "stock_rf.joblib"
LAGS = 10                                      # features: the last 10 daily returns (as in Session04_AI1)


class UnknownSymbol(Exception):
    pass


def make_features(closes):
    ret = pd.Series(closes).pct_change() * 100
    return pd.concat({f"lag{i}": ret.shift(i) for i in range(LAGS)}, axis=1)


@functools.cache                               # load the model once, at the first request
def load_model():
    return joblib.load(MODEL_PATH)


def predict_tomorrow(symbol):
    symbol = symbol.upper()
    prices = data.fetch_prices(symbol)                         # data layer: FMP
    if len(prices) < LAGS + 1:
        raise UnknownSymbol(symbol)
    data.save_prices(symbol, prices)                           # data layer: SQLite

    closes = [p["close"] for p in prices]
    X = make_features(closes).iloc[[-1]]                       # features of the newest day
    return_pct = float(load_model().predict(X)[0])             # the model: a function call in the same program

    prediction = {"symbol": symbol, "as_of": prices[-1]["date"], "close": closes[-1],
                  "return_pct": round(return_pct, 3),
                  "close_next": round(closes[-1] * (1 + return_pct / 100), 2)}
    data.save_prediction(prediction)                           # data layer: SQLite
    return {**prediction, "last_prices": prices[-10:]}


def history(symbol):
    return data.get_predictions(symbol.upper())
