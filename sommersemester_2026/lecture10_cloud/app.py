"""Streamlit entry point — cloud-ready Income Predictor (Lecture 10).

Same app as Lecture 09, but prepared for deployment on a PaaS (itdone3,
Heroku-style). The key difference: the **chat agent uses a local Ollama
server**, which does *not* exist on a PaaS. So the chat page is shown only
when ``ENABLE_CHAT`` is set (the default locally); in the cloud we leave it
off and ship the **form page only** — it needs no LLM and runs anywhere.

    Local  (ENABLE_CHAT=1, default):  Form + Chat (Ollama)
    Cloud  (ENABLE_CHAT=0):           Form only

Run locally:   streamlit run app.py
Run in cloud:  see Procfile — binds to $PORT, with ENABLE_CHAT=0.
"""

import os

import streamlit as st

st.set_page_config(
    page_title="Income Preditor",
    page_icon="💼",
    layout="centered",
)

# The chat page imports `ollama` and talks to a local Ollama server, so it is
# only useful where one is running. Default on locally, off in the cloud.
ENABLE_CHAT = os.getenv("ENABLE_CHAT", "1") == "1"

pages = [
    st.Page("form_page.py", title="Income prediction", icon="📝", default=True),
]
if ENABLE_CHAT:
    pages.append(st.Page("chat_page.py", title="Chat agent (Ollama)", icon="💬"))

st.navigation(pages).run()
