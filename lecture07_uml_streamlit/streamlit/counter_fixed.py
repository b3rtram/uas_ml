"""Block 3 — the same counter, fixed with session_state.

Run with:  streamlit run counter_fixed.py
session_state survives reruns, so the count now grows: 1, 2, 3, ...
"""
import streamlit as st

if "count" not in st.session_state:   # initialise once, do not overwrite
    st.session_state.username = ""

if st.button("Increment"):
    st.session_state.username = "Holzer"

st.write("Count:", st.session_state.count)
