"""STATUS: tell the user what is going on: messages, waiting, progress."""
import time

import streamlit as st

st.title("Status")

st.subheader("Messages")
st.success("st.success: prediction saved")
st.info("st.info: the market is closed, prices are from Friday")
st.warning("st.warning: only 8 days of prices, the model needs 11")
st.error("st.error: unknown symbol XYZ")
st.exception(ValueError("st.exception: shows an error with its type"))

st.subheader("Waiting")
if st.button("st.spinner"):
    with st.spinner("Loading prices ..."):
        time.sleep(2)
    st.write("Loaded.")

if st.button("st.progress"):
    bar = st.progress(0, text="Training ...")
    for i in range(1, 101):
        time.sleep(0.02)
        bar.progress(i, text=f"Training ... tree {i * 2} of 200")

if st.button("st.status"):
    with st.status("Predicting ...", expanded=True) as status:
        st.write("Fetching prices from FMP")
        time.sleep(1)
        st.write("Computing features")
        time.sleep(1)
        st.write("Running the model")
        time.sleep(1)
        status.update(label="Done", state="complete", expanded=False)

st.subheader("Small and fun")
c1, c2, c3 = st.columns(3)
if c1.button("st.toast"):
    st.toast("Prediction saved", icon="✅")      # a small note in the corner that goes away
if c2.button("st.balloons"):
    st.balloons()
if c3.button("st.snow"):
    st.snow()
