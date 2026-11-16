"""CHAT: chat elements. The 'bot' here is a few if statements; Session 4 showed how to put a real LLM behind it."""
import time

import streamlit as st

import demo_data

st.title("Chat")
st.caption("Try: 'price AAPL', 'hello', anything else.")

if "messages" not in st.session_state:         # the chat history survives the reruns
    st.session_state.messages = [{"role": "assistant", "content": "Hi! Ask me for a price, e.g. 'price MSFT'."}]


def answer(question):
    words = question.upper().split()
    for s in demo_data.SYMBOLS:
        if s in words:
            return f"The last (made-up) close of {s} is ${demo_data.prices()[s].iloc[-1]:.2f}."
    if "HELLO" in words or "HI" in words:
        return "Hello! I know AAPL, MSFT and NVDA."
    return f"I don't understand '{question}'. Try 'price AAPL'."


def stream(text):                              # yields word by word, like an LLM does
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.05)


for m in st.session_state.messages:            # show the history again in every run
    with st.chat_message(m["role"]):
        st.write(m["content"])

if question := st.chat_input("Your message"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)
    with st.chat_message("assistant"):
        reply = st.write_stream(stream(answer(question)))
    st.session_state.messages.append({"role": "assistant", "content": reply})
