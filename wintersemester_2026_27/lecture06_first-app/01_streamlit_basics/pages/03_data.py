"""DATA: tables, numbers and downloads."""
import streamlit as st

import demo_data

st.title("Data")
st.caption("Illustrative prices (random walk), not real ones.")
df = demo_data.prices()

st.subheader("st.metric")
for col, s in zip(st.columns(3), demo_data.SYMBOLS):
    last, before = df[s].iloc[-1], df[s].iloc[-2]
    col.metric(s, f"${last:.2f}", f"{(last / before - 1) * 100:+.2f} %", border=True)

st.subheader("st.dataframe: sort, search, resize, full screen")
summary = {"symbol": demo_data.SYMBOLS,
           "close": [df[s].iloc[-1] for s in demo_data.SYMBOLS],
           "last 30 days": [df[s].tail(30).tolist() for s in demo_data.SYMBOLS]}
st.dataframe(summary, hide_index=True, column_config={
    "close": st.column_config.NumberColumn("close", format="$%.2f"),
    "last 30 days": st.column_config.LineChartColumn("last 30 days"),      # a small chart in each cell
})

st.subheader("st.data_editor: the user edits the table")
portfolio = st.data_editor({"symbol": demo_data.SYMBOLS, "shares": [10, 5, 20]},
                           num_rows="dynamic", hide_index=True)
total = sum(n * df[s].iloc[-1] for s, n in zip(portfolio["symbol"], portfolio["shares"])
            if s in demo_data.SYMBOLS and n)
st.write(f"Portfolio value: **${total:,.2f}**")

st.subheader("st.table: static, everything visible")
last3 = df.tail(3).assign(date=df["date"].dt.strftime("%Y-%m-%d")).set_index("date")
st.table(last3.style.format("${:.2f}"))

st.subheader("st.json")
st.json({"symbol": "AAPL", "as_of": "2026-11-13", "return_pct": -0.012}, expanded=True)

st.download_button("st.download_button: prices as CSV", df.to_csv(index=False),
                   file_name="prices.csv", mime="text/csv")
