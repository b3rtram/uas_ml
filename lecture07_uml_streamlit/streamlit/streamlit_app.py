"""App entry point — multipage with st.navigation (Block 5).

We use EXPLICIT navigation (st.Page + st.navigation) rather than the magic
`pages/` folder, because that is what the lecture teaches. Run with:

    streamlit run streamlit_app.py
"""
import streamlit as st

st.set_page_config(page_title="Streamlit Deep Dive", layout="wide")

dashboard = st.Page("views/dashboard.py", title="Churn Dashboard", icon=":material/dashboard:")
agent = st.Page("views/agent.py", title="Agent", icon=":material/chat:")

pg = st.navigation([dashboard, agent])
pg.run()
