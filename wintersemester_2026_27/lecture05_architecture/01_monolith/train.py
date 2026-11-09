"""Train the model once:  python train.py   -> models/stock_rf.joblib
Same model as in Session04_AI1: 10 lagged returns -> tomorrow's return."""
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

import data
import logic

prices = data.fetch_prices("AAPL", days=12 * 365)
X = logic.make_features([p["close"] for p in prices])
table = X.assign(target=X["lag0"].shift(-1)).dropna()          # target = tomorrow's return

train, test = train_test_split(table, test_size=60, shuffle=False)   # time series: never shuffle
model = RandomForestRegressor(n_estimators=200, min_samples_leaf=20, random_state=42, n_jobs=-1)
model.fit(train.drop(columns="target"), train["target"])

pred = model.predict(test.drop(columns="target"))
print(f"MAE model    : {mean_absolute_error(test['target'], pred):.3f} % return")
print(f"MAE baseline : {mean_absolute_error(test['target'], [0.0] * len(test)):.3f} % return  (tomorrow = today)")

logic.MODEL_PATH.parent.mkdir(exist_ok=True)
joblib.dump(model, logic.MODEL_PATH)
print("saved", logic.MODEL_PATH)
