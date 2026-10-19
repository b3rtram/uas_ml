"""
app.py — Streamlit app: loads the trained LR model and shows
historical prices + a prediction for tomorrow.

Usage:
    streamlit run app.py

Prerequisite: model.pkl exists (run 'python train.py' first).
"""
import streamlit as st
import yfinance as yf
import pandas as pd
import joblib
import plotly.graph_objects as go
from pathlib import Path


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Stock Price Predictor",
    page_icon="📈",
    layout="wide",
)
st.title("📈 Stock Price Predictor")
st.caption("Gradient boosting on stock prices — Lecture 5")


# ---------------------------------------------------------------------------
# Cached helpers
# ---------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_data(ticker: str, days: int) -> pd.DataFrame:
    """Fetch historical data from Yahoo Finance and add MA7."""
    df = yf.Ticker(ticker).history(period=f"{days}d")
    df["MA7"] = df["Close"].rolling(7).mean()
    return df.dropna()


@st.cache_resource
def load_model():
    """Load the model produced by train.py."""
    if not Path("model.pkl").exists():
        return None
    return joblib.load("model.pkl")


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.header("Settings")
ticker = st.sidebar.text_input("Ticker", "AAPL").upper()
days = st.sidebar.slider("History (days)", 30, 365, 90)


# ---------------------------------------------------------------------------
# Load model
# ---------------------------------------------------------------------------
model = load_model()
if model is None:
    st.error(
        "No trained model found. Please run `python train.py` first."
    )
    st.stop()


# ---------------------------------------------------------------------------
# Fetch data
# ---------------------------------------------------------------------------
try:
    df = fetch_data(ticker, days)
except Exception as e:
    st.error(f"Could not fetch data for {ticker}: {e}")
    st.stop()

if df.empty:
    st.warning(f"No data found for '{ticker}'.")
    st.stop()


# ---------------------------------------------------------------------------
# Compute prediction
# ---------------------------------------------------------------------------
latest = df.iloc[-1]
features = pd.DataFrame(
    [[latest["Close"], latest["Volume"], latest["MA7"]]],
    columns=["Close", "Volume", "MA7"],
)
prediction = float(model.predict(features)[0])
next_date = df.index[-1] + pd.Timedelta(days=1)


# ---------------------------------------------------------------------------
# Chart
# ---------------------------------------------------------------------------
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.index, y=df["Close"],
    name="Close", mode="lines",
    line=dict(color="#6366f1", width=2),
))
fig.add_trace(go.Scatter(
    x=[next_date], y=[prediction],
    name="Prediction",
    mode="markers",
    marker=dict(size=18, color="#f59e0b", symbol="star"),
))
fig.update_layout(
    title=f"{ticker} — close + prediction for tomorrow",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    height=500,
    hovermode="x unified",
    plot_bgcolor="#fafafa",
    paper_bgcolor="#fafafa",
    font=dict(color="#1f2937"),
)
st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Prediction metric
# ---------------------------------------------------------------------------
delta = prediction - float(latest["Close"])
col1, col2 = st.columns(2)
col1.metric(
    label=f"Last close ({df.index[-1].strftime('%Y-%m-%d')})",
    value=f"${float(latest['Close']):.2f}",
)
col2.metric(
    label=f"Prediction for {next_date.strftime('%Y-%m-%d')}",
    value=f"${prediction:.2f}",
    delta=f"{delta:+.2f} USD",
)


# ---------------------------------------------------------------------------
# Model inspection
# ---------------------------------------------------------------------------
with st.expander("🔍 What did the model learn?"):
    st.write("**Feature importances:**")
    for name, imp in zip(["Close", "Volume", "MA7"], model.feature_importances_):
        st.write(f"- `{name}` = {imp:.4f}")

    if ticker != "AAPL":
        st.warning(
            f"⚠️ Note: this model was trained on **AAPL**. "
            f"Predictions for **{ticker}** are therefore not reliable — "
            f"see the homework!"
        )

st.caption(
    "⚠️ Teaching example — please don't use this for real investment decisions."
)
