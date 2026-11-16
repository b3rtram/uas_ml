"""Streamlit basics: each page shows one facet of Streamlit. The full Stock App is in ../03_stock_app.
Start:  streamlit run app.py      then open http://localhost:8501"""
import streamlit as st

st.set_page_config(page_title="Streamlit tour", page_icon="🎈", layout="wide")

pages = {
    "Elements": [
        st.Page("pages/01_text.py", title="Text", icon="📝", default=True),
        st.Page("pages/02_widgets.py", title="Widgets", icon="🎛️"),
        st.Page("pages/03_data.py", title="Data", icon="🧮"),
        st.Page("pages/04_charts.py", title="Charts", icon="📈"),
        st.Page("pages/05_layout.py", title="Layout", icon="🧱"),
        st.Page("pages/06_status.py", title="Status", icon="🚦"),
    ],
    "How Streamlit runs": [
        st.Page("pages/07_rerun_state.py", title="Rerun and state", icon="🔁"),
        st.Page("pages/08_cache.py", title="Caching", icon="⚡"),
        st.Page("pages/09_chat.py", title="Chat", icon="💬"),
    ],
}

st.sidebar.caption("Every page is one file in pages/. Open it next to the browser.")
st.navigation(pages).run()                     # runs the page the user picked in the sidebar
