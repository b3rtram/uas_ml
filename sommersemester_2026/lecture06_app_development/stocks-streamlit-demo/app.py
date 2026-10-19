"""
app.py — Streamlit all-in-one stock forecaster.

Same use case as Demo 1: add tickers to a portfolio, run Prophet forecasts.
But here it's ONE PYTHON FILE instead of seven files across three languages.

Streamlit handles for you:
  - the web server         (no uvicorn)
  - the frontend/backend split (no fetch, no HTTP)
  - event handling         (no addEventListener)
  - DOM updates            (no innerHTML, no appendChild)
  - chart rendering        (one st.plotly_chart call)
  - state management       (st.session_state)

Run with:
    streamlit run app.py
"""

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from prophet import Prophet

logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
logging.getLogger("prophet").setLevel(logging.WARNING)

DB_FILE = Path(__file__).parent / "portfolio.db"


# ================================================================
# DATABASE — same SQLite, same schema as Demo 1's db.py
# ================================================================

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker   TEXT    NOT NULL UNIQUE,
                added_at TEXT    NOT NULL
            )
        """)


def add_to_portfolio(ticker):
    ticker = ticker.upper().strip()
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    with get_db() as conn:
        conn.execute(
            "INSERT INTO portfolio (ticker, added_at) VALUES (?, ?)",
            (ticker, now),
        )


def list_portfolio():
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM portfolio ORDER BY added_at ASC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_from_portfolio(stock_id):
    with get_db() as conn:
        conn.execute("DELETE FROM portfolio WHERE id = ?", (stock_id,))


# ================================================================
# DATA — same yfinance wrapper as Demo 1's data.py
# ================================================================

def fetch_history(ticker, days=365):
    end = datetime.now()
    start = end - timedelta(days=days)
    df = yf.download(
        ticker,
        start=start.strftime("%Y-%m-%d"),
        end=end.strftime("%Y-%m-%d"),
        progress=False,
        auto_adjust=True,
    )
    if df.empty:
        raise ValueError(f"No data for ticker '{ticker}'.")
    close = df["Close"].squeeze()
    return pd.DataFrame({
        "ds": pd.to_datetime(close.index).tz_localize(None),
        "y": close.values.astype(float),
    }).reset_index(drop=True)


# ================================================================
# FORECAST — same Prophet wrapper as Demo 1's forecast.py
# ================================================================

def make_forecast(history, horizon_days=30):
    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
        interval_width=0.80,
    )
    model.fit(history)
    future = model.make_future_dataframe(periods=horizon_days)
    forecast = model.predict(future)
    last_hist = history["ds"].max()
    forecast = forecast[forecast["ds"] > last_hist]
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]]


# ================================================================
# UI — the part that makes the contrast with Demo 1 obvious
# ================================================================

init_db()

st.set_page_config(page_title="Stock forecast — Streamlit", page_icon="📈", layout="wide")
st.title("📈 Stock forecast")
st.caption("Streamlit all-in-one — same app as Demo 1, one Python file.")


# ---------- Portfolio panel ----------

st.subheader("Your portfolio")

# Replaces in Demo 1:  <form id="add-form"> in index.html
#                    + addForm.addEventListener("submit", ...) in app.js
#                    + apiAddStock() fetch call in app.js
with st.form("add-form", clear_on_submit=True):
    cols = st.columns([4, 1])
    with cols[0]:
        new_ticker = st.text_input(
            "Ticker", placeholder="e.g. AAPL, MSFT, SAP.DE",
            label_visibility="collapsed",
        )
    with cols[1]:
        submitted = st.form_submit_button(
            "Add", type="primary", use_container_width=True,
        )

if submitted and new_ticker.strip():
    try:
        # Direct function call — no HTTP, no JSON serialization
        add_to_portfolio(new_ticker)
        st.rerun()
    except sqlite3.IntegrityError:
        st.error(f"'{new_ticker.upper()}' is already in the portfolio")


# Replaces in Demo 1: the entire renderPortfolio() function in app.js —
# the document.createElement("li") loop with innerHTML strings.
portfolio = list_portfolio()
if not portfolio:
    st.caption("Add a ticker to get started.")
else:
    for item in portfolio:
        cols = st.columns([5, 1])
        # Clicking the ticker selects it for forecasting.
        # Replaces the delegated click handler + data-ticker attribute in Demo 1.
        if cols[0].button(
            item["ticker"], key=f"t-{item['id']}",
            use_container_width=True,
        ):
            st.session_state["selected"] = item["ticker"]
        if cols[1].button("✕", key=f"d-{item['id']}", help="Remove"):
            delete_from_portfolio(item["id"])
            if st.session_state.get("selected") == item["ticker"]:
                st.session_state.pop("selected", None)
            st.rerun()


# ---------- Forecast panel ----------

selected = st.session_state.get("selected")
if selected:
    st.divider()
    st.subheader(f"{selected} forecast")

    # Replaces in Demo 1: the entire showForecast() async chain —
    # apiGetForecast fetch + JSON parse + status messages.
    with st.spinner(f"Fetching {selected} and running Prophet…"):
        try:
            history = fetch_history(selected, 365)
            forecast = make_forecast(history, 30)
        except Exception as e:
            st.error(str(e))
            st.stop()

    # Stats — replaces in Demo 1: the three statXxx.textContent assignments
    # plus the change-up/down className flipping.
    latest = float(history["y"].iloc[-1])
    predicted = float(forecast["yhat"].iloc[-1])
    lower = float(forecast["yhat_lower"].iloc[-1])
    upper = float(forecast["yhat_upper"].iloc[-1])
    change_pct = (predicted - latest) / latest * 100

    cols = st.columns(3)
    cols[0].metric("Latest price", f"${latest:.2f}")
    cols[1].metric(
        "Predicted in 30 days",
        f"${predicted:.2f}",
        f"{change_pct:+.1f}%",
    )
    cols[2].metric("80% confidence range", f"${lower:.2f} – ${upper:.2f}")

    # Chart — replaces in Demo 1: the entire drawChart() function with
    # Chart.js setup, dataset construction, axes config, legend filtering.
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(forecast["ds"]) + list(forecast["ds"])[::-1],
        y=list(forecast["yhat_upper"]) + list(forecast["yhat_lower"])[::-1],
        fill="toself", fillcolor="rgba(15, 118, 110, 0.15)",
        line=dict(width=0), name="Confidence band", hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=history["ds"], y=history["y"],
        mode="lines", name="Historical",
        line=dict(color="#1E293B", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=forecast["ds"], y=forecast["yhat"],
        mode="lines", name="Forecast",
        line=dict(color="#0F766E", width=2, dash="dot"),
    ))
    fig.update_layout(
        height=400, hovermode="x unified",
        margin=dict(l=0, r=0, t=30, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)
