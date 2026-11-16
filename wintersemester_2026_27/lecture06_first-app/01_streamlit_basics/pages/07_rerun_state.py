"""RERUN AND STATE: the most important idea in Streamlit.
After every click Streamlit runs the whole file again from the top. Normal variables start fresh each time."""
from datetime import datetime

import streamlit as st

st.title("Rerun and state")
st.caption(f"This page was last run completely at {datetime.now():%H:%M:%S}.")

st.subheader("1 · A normal variable forgets")
count = 0
if st.button("+1 (normal variable)"):
    count += 1
st.write(f"count = {count}  (never more than 1: each run starts again with count = 0)")

st.subheader("2 · st.session_state remembers")
if "clicks" not in st.session_state:           # only in the very first run of this browser tab
    st.session_state.clicks = 0
if st.button("+1 (session_state)"):
    st.session_state.clicks += 1
st.write(f"st.session_state.clicks = {st.session_state.clicks}")


st.subheader("3 · Callback: runs before the page is rebuilt")
def reset():
    st.session_state.clicks = 0


st.button("Reset", on_click=reset)

st.subheader("4 · A widget with key= lives in session_state")
st.text_input("Symbol", key="symbol", value="AAPL")
st.write(f'st.session_state["symbol"] = {st.session_state["symbol"]!r}')

st.subheader("5 · st.form: one rerun on submit, not on every change")
with st.form("order"):
    symbol = st.selectbox("Symbol", ["AAPL", "MSFT", "NVDA"])
    shares = st.number_input("Shares", min_value=1, value=10)
    submitted = st.form_submit_button("Buy")
if submitted:
    st.success(f"Order: {shares} × {symbol}")


st.subheader("6 · st.fragment: rerun only a part of the page")
@st.fragment
def live_clock():
    st.button("Refresh only this box")
    st.write(f"Fragment run at {datetime.now():%H:%M:%S}. The time in the caption on top does not change.")


with st.container(border=True):
    live_clock()

st.subheader("7 · st.query_params: state in the URL")
st.write(f"st.query_params = {dict(st.query_params)}. Try adding ?symbol=MSFT to the URL.")

st.subheader("All of session_state")
st.write(st.session_state)
