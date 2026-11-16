"""CACHING: because every click runs the whole file again, slow work must not be repeated each time."""
import time

import numpy as np
import streamlit as st
from sklearn.ensemble import RandomForestRegressor

st.title("Caching")
st.caption("Every click reruns the page. Without a cache the slow functions would run every time.")


@st.cache_data                                 # for DATA: result is stored per argument value
def load_prices(symbol):
    time.sleep(2)                              # stands in for a slow download
    return list(np.random.default_rng(len(symbol)).normal(100, 5, 5).round(2))


@st.cache_resource                             # for OBJECTS that are shared: models, database connections
def load_model():
    time.sleep(2)                              # stands in for loading or training a model
    rng = np.random.default_rng(0)
    X = rng.normal(size=(500, 3))
    return RandomForestRegressor(n_estimators=50, random_state=0).fit(X, X @ [1.0, 2.0, 3.0])


symbol = st.selectbox("Symbol", ["AAPL", "MSFT", "NVDA"])

t0 = time.perf_counter()
prices = load_prices(symbol)
st.write(f"load_prices({symbol!r}) took **{time.perf_counter() - t0:.3f} s**: {prices}")

t0 = time.perf_counter()
model = load_model()
st.write(f"load_model() took **{time.perf_counter() - t0:.3f} s**, object id {id(model)} (always the same object)")

st.info("First time per symbol: 2 s. Then 0.00 s. Switch to a new symbol: 2 s again, back: 0.00 s.")
st.markdown("""
| | `@st.cache_data` | `@st.cache_resource` |
|---|---|---|
| for | data: DataFrames, lists, API results | objects: ML models, database connections |
| returns | a **copy** for every caller | the **same object** for everyone |
| typical | `fetch_prices(symbol)` | `load_model()` |
""")

if st.button("Clear both caches"):
    load_prices.clear()
    load_model.clear()
    st.rerun()
