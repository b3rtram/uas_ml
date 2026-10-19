"""Block 2 — the counter that forgets.

Run with:  streamlit run counter_broken.py
Click "Increment" a few times. It stays at 1, never 2, 3, 4 ...
Why? `count = 0` runs again on EVERY click, because the whole script reruns.
"""
import streamlit as st

count = 0
if st.button("Increment"):
    count += 1
st.write("Count:", count)
