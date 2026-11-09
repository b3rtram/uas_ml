"""BUSINESS LAYER of the backend: prices -> ask the ML service -> prediction.
The only change against 01_monolith/logic.py: the model is no longer in this program.
We send the prices to the ML service over REST. No pandas, no scikit-learn needed here."""
import os

import requests

import data

ML_URL = os.getenv("ML_URL", "http://127.0.0.1:8001")      # where the ML service runs
LAGS = 10                                                  # the ML service needs LAGS + 1 prices


class UnknownSymbol(Exception):
    pass


class ModelUnavailable(Exception):
    pass


def ask_ml_service(closes):
    try:
        r = requests.post(f"{ML_URL}/predict", json={"closes": closes[-(LAGS + 1):]}, timeout=5)
        r.raise_for_status()
    except requests.RequestException as e:                 # not running, too slow, or answered with an error
        raise ModelUnavailable(str(e))
    return r.json()["return_pct"]


def predict_tomorrow(symbol):
    symbol = symbol.upper()
    prices = data.fetch_prices(symbol)                     # data layer: FMP
    if len(prices) < LAGS + 1:
        raise UnknownSymbol(symbol)
    data.save_prices(symbol, prices)                       # data layer: SQLite

    closes = [p["close"] for p in prices]
    return_pct = ask_ml_service(closes)                    # was: load_model().predict(X), now a REST call

    prediction = {"symbol": symbol, "as_of": prices[-1]["date"], "close": closes[-1],
                  "return_pct": round(return_pct, 3),
                  "close_next": round(closes[-1] * (1 + return_pct / 100), 2)}
    data.save_prediction(prediction)                       # data layer: SQLite
    return {**prediction, "last_prices": prices[-10:]}


def history(symbol):
    return data.get_predictions(symbol.upper())
