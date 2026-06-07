"""Agent page — the Ollama notebook agent, now with a UI (Block 6).

The whole chat loop stands on two ideas from earlier in the lecture:
  * the script reruns top to bottom on every message
  * so the conversation must live in st.session_state to survive

`agent_stream` is the SAME generator idea you used in the notebook: it wraps
`ollama.chat(..., stream=True)` and yields text chunks. If Ollama is not
running, it falls back to a fake stream so the demo never breaks in class.
"""
import time

import streamlit as st

MODEL = "gemma4"

st.title("Talk to your Agent")
st.caption("The Ollama agent from your notebook — now with a face.")


def agent_stream(messages):
    """Yield text chunks. Wraps Ollama; falls back to a fake stream."""
    try:
        import ollama

        stream = ollama.chat(model=MODEL, messages=messages, stream=True)
        for chunk in stream:
            yield chunk["message"]["content"]
    except Exception:
        demo = (
            "Ollama is not reachable, so this is a demo stream. "
            "Run `ollama serve` and `ollama pull gemma4`, then refresh."
        )
        for word in demo.split():
            yield word + " "
            time.sleep(0.03)


# The conversation history lives in session_state so it survives reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Redraw the whole history on every rerun.
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# chat_input is pinned to the bottom of the page.
if prompt := st.chat_input("Ask the agent…"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # write_stream renders the typewriter effect and returns the full text.
        answer = st.write_stream(agent_stream(st.session_state.messages))

    st.session_state.messages.append({"role": "assistant", "content": answer})
