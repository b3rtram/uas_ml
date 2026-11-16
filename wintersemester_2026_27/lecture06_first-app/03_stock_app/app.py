"""STOCK APP: the whole chain in one Streamlit file: FMP API -> prices -> chart -> (your ML model).
Start:  streamlit run app.py      Needs FMP_API_KEY=... in the .env file in the repo root (as in Session 2).

The file has the three layers from Session 5, top to bottom: data, logic (ML), presentation (UI)."""
import os
from datetime import date, timedelta

import altair as alt
import pandas as pd
import requests
import streamlit as st
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))          # the API key comes from .env, never from the code
FMP_URL = "https://financialmodelingprep.com/stable/historical-price-eod/light"


# ---- DATA LAYER: get prices from FMP --------------------------------------------------------------
@st.cache_data(ttl="1h", show_spinner="Fetching prices from FMP ...")    # same symbol again: no new download
def fetch_prices(symbol, days):
    """DataFrame with the columns date and close, oldest day first. Empty = unknown symbol."""
    start = (date.today() - timedelta(days=days)).isoformat()
    r = requests.get(FMP_URL, params={"symbol": symbol, "from": start, "apikey": os.getenv("FMP_API_KEY")},
                     timeout=10)
    r.raise_for_status()
    rows = [{"date": row["date"], "close": row["price"]} for row in reversed(r.json())]
    return pd.DataFrame(rows, columns=["date", "close"]).astype({"date": "datetime64[ns]"})


# ---- LOGIC LAYER: the place for your ML model -----------------------------------------------------
def predict_next_close(prices):
    """PLACEHOLDER. Gets all prices (DataFrame date, close), returns the predicted close for the next day.

    Right now: the naive baseline 'tomorrow = today'. Replace it with your model, for example the
    RandomForest from Session 4 / Session 5:
        model = load_model()                   # with @st.cache_resource, so it is loaded only once
        X = make_features(prices["close"])     # the last 10 daily returns
        return_pct = model.predict(X.iloc[[-1]])[0]
        return prices["close"].iloc[-1] * (1 + return_pct / 100)
    """
    return prices["close"].iloc[-1]


# ---- PRESENTATION LAYER: the page -----------------------------------------------------------------
st.set_page_config(page_title="Stock App", page_icon="💹", layout="wide")
st.title("💹 Stock App")

if not os.getenv("FMP_API_KEY"):
    st.error("FMP_API_KEY missing: put FMP_API_KEY=... into the .env file in the repo root.")
    st.stop()                                  # nothing below this line runs

with st.sidebar:
    symbol = st.text_input("Symbol", value=st.query_params.get("symbol", "AAPL")).strip().upper()
    days = st.slider("Days", 30, 730, 180)
    show_table = st.checkbox("Show the prices as a table")

try:
    prices = fetch_prices(symbol, days)
except requests.RequestException as e:
    st.error(f"FMP did not answer: {e}")
    st.stop()
if len(prices) < 2:
    st.error(f"No prices for {symbol!r}. Is the symbol right?")
    st.stop()
st.query_params["symbol"] = symbol             # the URL remembers the symbol: ?symbol=MSFT

close, before = prices["close"].iloc[-1], prices["close"].iloc[-2]
as_of = prices["date"].iloc[-1].date().isoformat()
first = prices["close"].iloc[0]

c1, c2, c3 = st.columns(3)
c1.metric(f"{symbol} close on {as_of}", f"${close:.2f}", f"{(close / before - 1) * 100:+.2f} % vs. day before",
          border=True)
c2.metric(f"Change over {days} days", f"{(close / first - 1) * 100:+.1f} %", border=True)
c3.metric("Range", f"${prices['close'].min():.2f} – ${prices['close'].max():.2f}", border=True)

st.subheader("Price")
st.altair_chart(alt.Chart(prices).mark_line().encode(
    x=alt.X("date", title=None),
    y=alt.Y("close", title="close in $", scale=alt.Scale(zero=False)),   # don't start the axis at 0
    tooltip=["date", "close"]))

st.subheader("Prediction for the next trading day")
with st.container(border=True):
    st.caption("ML PLACEHOLDER: `predict_next_close()` in app.py. Right now it says 'tomorrow = today'. "
               "Put your model there; this box shows its result without any other change.")
    next_close = predict_next_close(prices)
    p1, p2 = st.columns(2)
    p1.metric("Predicted close", f"${next_close:.2f}", f"{next_close - close:+.2f} $")
    p2.metric("Predicted return", f"{(next_close / close - 1) * 100:+.3f} %")

if show_table:
    st.dataframe(prices.sort_values("date", ascending=False), hide_index=True)
st.download_button("Download prices as CSV", prices.to_csv(index=False), f"{symbol}_prices.csv", "text/csv")
st.caption("Prices: Financial Modeling Prep. Not investment advice.")
