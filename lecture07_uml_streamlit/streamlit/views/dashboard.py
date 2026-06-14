"""Churn dashboard — the Dashboard component from the Block 1 blueprint.

Demonstrates: sidebar inputs, st.columns (KPIs), st.tabs, a chart, st.dataframe,
and the cached model loaded via cache_resource.
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from model_utils import load_data, load_model

st.title("Customer Churn Dashboard")

model = load_model()   # cached: the .pkl is loaded ONCE, not on every rerun
data = load_data()     # cached data

# --- Sidebar: the inputs for one customer ---
st.sidebar.header("Customer")
tenure = st.sidebar.slider("Tenure (months)", 0, 72, 12)
monthly = st.sidebar.slider("Monthly charges ($)", 20.0, 120.0, 70.0)
contract = st.sidebar.selectbox("Contract", ["Month-to-month", "One year", "Two year"])
internet = st.sidebar.selectbox("Internet service", ["DSL", "Fiber optic", "No"])

input_df = pd.DataFrame(
    [{"tenure": tenure, "MonthlyCharges": monthly, "Contract": contract, "InternetService": internet}]
)
prob = float(model.predict_proba(input_df)[0])

# --- KPI row with st.columns ---
c1, c2, c3 = st.columns(3)
c1.metric("Churn probability", f"{prob:.0%}")
c2.metric("Risk level", "High" if prob > 0.5 else "Low")
c3.metric("Customers in data", f"{len(data):,}")

# --- Tabs ---
tab_pred, tab_data = st.tabs(["Prediction", "Data overview"])

with tab_pred:
    st.subheader("This customer")
    fig = px.bar(
        x=["Stay", "Churn"],
        y=[1 - prob, prob],
        labels={"x": "", "y": "Probability"},
        range_y=[0, 1],
        color=["Stay", "Churn"],
        color_discrete_sequence=["#2e7d32", "#c62828"],
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, width="stretch")

with tab_data:
    st.subheader("Churn rate by contract type")
    rate = data.groupby("Contract", as_index=False)["Churn"].mean()
    st.plotly_chart(
        px.bar(rate, x="Contract", y="Churn", range_y=[0, 1], labels={"Churn": "Churn rate"}),
        width="stretch",
    )
    st.dataframe(data, width="stretch")
