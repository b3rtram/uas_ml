"""
train.py — Train a linear regression model on AAPL stock prices.

Saves the learned model to model.pkl so app.py can load it.

Usage:
    python train.py
"""
import yfinance as yf
import joblib
from sklearn.linear_model import LinearRegression


# ---------------------------------------------------------------------------
# 1. Fetch data
# ---------------------------------------------------------------------------
print("Fetching AAPL data from Yahoo Finance ...")
df = yf.Ticker("AAPL").history(period="2y")
print(f"  Loaded {len(df)} trading days.")


# ---------------------------------------------------------------------------
# 2. Build features
# ---------------------------------------------------------------------------
# Three features: today's close, today's volume, 7-day moving average.
# Target: tomorrow's close — i.e. the Close one row down.
df["MA7"] = df["Close"].rolling(7).mean()
df["Target"] = df["Close"].shift(-1)
df = df.dropna()

X = df[["Close", "Volume", "MA7"]]
y = df["Target"]

print(f"  {len(X)} training examples with {X.shape[1]} features.")


# ---------------------------------------------------------------------------
# 3. Train the model
# ---------------------------------------------------------------------------
print("\nTraining LinearRegression ...")
model = LinearRegression()
model.fit(X, y)


# ---------------------------------------------------------------------------
# 4. What did the model learn?
# ---------------------------------------------------------------------------
print("\nThe model learned the following parameters:")
for name, w in zip(X.columns, model.coef_):
    print(f"  w_{name:<8} = {w:>14.6f}")
print(f"  b (intercept) = {model.intercept_:>14.4f}")
print(f"\n  R² on training data: {model.score(X, y):.4f}")


# ---------------------------------------------------------------------------
# 5. Save the model
# ---------------------------------------------------------------------------
joblib.dump(model, "model.pkl")
print("\nModel saved: model.pkl")
print("  --> Now run 'streamlit run app.py' to use it.")
