"""The model: features and prediction. Same code as in 01_monolith/logic.py, now in its own service."""
from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).parent / "models" / "stock_rf.joblib"
LAGS = 10                                      # features: the last 10 daily returns


def make_features(closes):
    ret = pd.Series(closes).pct_change() * 100
    return pd.concat({f"lag{i}": ret.shift(i) for i in range(LAGS)}, axis=1)


def load_model():
    return joblib.load(MODEL_PATH)


def predict_return(model, closes):
    """closes: at least LAGS + 1 prices, oldest first -> predicted return for the next day in %."""
    X = make_features(closes).iloc[[-1]]       # features of the newest day
    return float(model.predict(X)[0])
