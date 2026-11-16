"""LAYOUT: where elements go. Without layout everything is stacked top to bottom."""
import time

import streamlit as st

st.title("Layout")

st.sidebar.subheader("st.sidebar")
st.sidebar.slider("A widget in the sidebar", 0, 10, 5)

st.subheader("st.columns")
a, b, c = st.columns([2, 1, 1], border=True)   # widths 2 : 1 : 1
a.write("wide column")
b.write("narrow")
c.write("narrow")

st.subheader("st.tabs")
t1, t2 = st.tabs(["First tab", "Second tab"])
t1.write("Both tabs are built in every run, the browser only shows one.")
t2.write("Content of the second tab.")

st.subheader("st.expander")
with st.expander("Details (click to open)"):
    st.write("Good for things most users don't need: raw data, explanations, settings.")

st.subheader("st.container")
with st.container(border=True):
    st.write("A box that groups elements.")
    st.button("A button inside the box")

st.subheader("st.popover")
with st.popover("Settings"):
    st.checkbox("Show volume")
    st.checkbox("Show moving average")


@st.dialog("st.dialog")
def confirm(symbol):
    st.write(f"Really remove {symbol} from the watchlist?")
    if st.button("Yes, remove"):
        st.rerun()                             # closes the dialog


st.subheader("st.dialog")
if st.button("Remove AAPL"):
    confirm("AAPL")

st.subheader("st.empty: one slot whose content is replaced")
if st.button("Count down"):
    slot = st.empty()
    for i in range(3, 0, -1):
        slot.write(f"{i} ...")
        time.sleep(1)
    slot.write("Done.")
