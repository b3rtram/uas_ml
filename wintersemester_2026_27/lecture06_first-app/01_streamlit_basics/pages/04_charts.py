"""CHARTS: Streamlit's own charts (one line each) and charts from other libraries."""
import altair as alt
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import streamlit as st

import demo_data

st.title("Charts")
st.caption("Illustrative prices (random walk), not real ones.")
df = demo_data.prices()
returns = df.set_index("date").pct_change().mul(100).dropna()     # daily returns in %

st.subheader("Built in: one line each")
c1, c2 = st.columns(2)
c1.write("st.line_chart")
c1.line_chart(df, x="date", y=demo_data.SYMBOLS)
c2.write("st.area_chart")
c2.area_chart(df, x="date", y="AAPL")
c1.write("st.bar_chart: AAPL daily return in %")
c1.bar_chart(returns["AAPL"].tail(30))
c2.write("st.scatter_chart: AAPL vs. MSFT return")
c2.scatter_chart(returns, x="AAPL", y="MSFT")

st.write("st.map: stock exchanges")
st.map(pd.DataFrame({"lat": [50.1155, 40.7069, 51.5155, 35.6828],
                     "lon": [8.6745, -74.0113, -0.0995, 139.7788]}), zoom=0, size=150_000, color="#C2410C")

st.subheader("Other libraries: more control")
tab_alt, tab_plotly, tab_mpl = st.tabs(["Altair", "Plotly", "Matplotlib"])
with tab_alt:
    long = df.melt("date", var_name="symbol", value_name="close")
    st.altair_chart(alt.Chart(long).mark_line().encode(x="date", y=alt.Y("close", scale=alt.Scale(zero=False)),
                                                       color="symbol", tooltip=["date", "symbol", "close"]))
with tab_plotly:
    st.plotly_chart(px.histogram(returns, x="AAPL", nbins=30, title="AAPL: how often which daily return"))
with tab_mpl:
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(df["date"], df["AAPL"])
    ax.set_ylabel("AAPL close in $")
    st.pyplot(fig)                             # the same plots as in the notebooks
