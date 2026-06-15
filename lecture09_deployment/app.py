"""Streamlit entry point — Adult / Census Income deployment demo.

Two pages:
  1. A form that feeds the saved model directly.
  2. A chat agent (via Ollama) that calls the same model through a tool.

Run with:  streamlit run app.py
"""

import streamlit as st

st.set_page_config(
    page_title="Income Predictor",
    page_icon="💼",
    layout="centered",
)

pages = [
    st.Page("form_page.py", title="Income prediction", icon="📝", default=True),
    st.Page("chat_page.py", title="Chat agent (Ollama)", icon="💬"),
]

st.navigation(pages).run()
