"""WIDGETS: every widget returns its current value. Change one, and Streamlit runs this whole file again."""
import pandas as pd
import streamlit as st

st.title("Widgets")
st.caption("Change a widget: Streamlit runs this file again from the top, now with the new value.")

left, right = st.columns(2)
with left:
    clicked = st.button("st.button")                       # True only in the run right after the click
    agree = st.checkbox("st.checkbox")
    on = st.toggle("st.toggle")
    chart = st.radio("st.radio", ["Line", "Bar"], horizontal=True)
    symbol = st.selectbox("st.selectbox", ["AAPL", "MSFT", "NVDA"])
    symbols = st.multiselect("st.multiselect", ["AAPL", "MSFT", "NVDA"], default=["AAPL"])
    period = st.pills("st.pills", ["1M", "3M", "1Y"], default="3M")
    view = st.segmented_control("st.segmented_control", ["Price", "Return"], default="Price")
    st.caption("st.feedback")
    stars = st.feedback("stars")                           # 0..4, None before the first click
with right:
    days = st.slider("st.slider", 10, 250, 60)
    low, high = st.slider("st.slider with two ends", 0.0, 100.0, (25.0, 75.0))
    risk = st.select_slider("st.select_slider", ["low", "medium", "high"], value="medium")
    amount = st.number_input("st.number_input", min_value=0, value=1000, step=100)
    name = st.text_input("st.text_input", placeholder="your name")
    note = st.text_area("st.text_area", height=80)
    day = st.date_input("st.date_input")
    color = st.color_picker("st.color_picker", "#C2410C")
upload = st.file_uploader("st.file_uploader (a CSV file)", type="csv")

st.divider()
st.subheader("What the widgets returned in this run")
values = {"st.button": clicked, "st.checkbox": agree, "st.toggle": on, "st.radio": chart,
          "st.selectbox": symbol, "st.multiselect": symbols, "st.pills": period,
          "st.segmented_control": view, "st.feedback": stars, "st.slider": days,
          "st.slider (range)": (low, high), "st.select_slider": risk, "st.number_input": amount,
          "st.text_input": name, "st.text_area": note, "st.date_input": day, "st.color_picker": color}
st.table(pd.DataFrame({"widget": values.keys(), "value": [repr(v) for v in values.values()]}).set_index("widget"))

if upload is not None:                                     # None until a file is uploaded
    st.write(f"{upload.name}: first rows")
    st.dataframe(pd.read_csv(upload).head())
