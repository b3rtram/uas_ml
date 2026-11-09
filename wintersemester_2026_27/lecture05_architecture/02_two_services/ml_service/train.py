"""Train the model once:  python train.py   -> models/stock_rf.joblib
The ML service gets its own training data from FMP: it doesn't share code with the backend.
Same 12 years of AAPL as 01_monolith/train.py, so both give the same model."""
import os
from datetime import date, timedelta

import joblib
import requests
from dotenv import find_dotenv, load_dotenv
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

import model

load_dotenv(find_dotenv(usecwd=True))
start = (date.today() - timedelta(days=12 * 365)).isoformat()
r = requests.get("https://financialmodelingprep.com/stable/historical-price-eod/light",
                 params={"symbol": "AAPL", "from": start, "apikey": os.environ["FMP_API_KEY"]}, timeout=30)
r.raise_for_status()
closes = [row["price"] for row in reversed(r.json())]      # oldest first

X = model.make_features(closes)
table = X.assign(target=X["lag0"].shift(-1)).dropna()      # target = tomorrow's return

train, test = train_test_split(table, test_size=60, shuffle=False)   # time series: never shuffle
rf = RandomForestRegressor(n_estimators=200, min_samples_leaf=20, random_state=42, n_jobs=-1)
rf.fit(train.drop(columns="target"), train["target"])

pred = rf.predict(test.drop(columns="target"))
print(f"MAE model    : {mean_absolute_error(test['target'], pred):.3f} % return")
print(f"MAE baseline : {mean_absolute_error(test['target'], [0.0] * len(test)):.3f} % return  (tomorrow = today)")

model.MODEL_PATH.parent.mkdir(exist_ok=True)
joblib.dump(rf, model.MODEL_PATH)
print("saved", model.MODEL_PATH)
