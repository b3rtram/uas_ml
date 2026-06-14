"""Page 2 — chat agent (Ollama) that calls the model through a tool.

The agent logic lives in ``agent.py`` (UI-independent, shared with the Discord
bot). This file is only the Streamlit front-end around it.
"""

import ollama
import streamlit as st

from agent import DEFAULT_MODEL, run_agent


def render_tool_steps(tool_steps):
    for step in tool_steps:
        with st.expander(f"🔧 Tool-Aufruf: `{step['tool']}`"):
            st.write("**Argumente (vom Agenten erzeugt)**")
            st.json(step["args"])
            st.write("**Ergebnis (vom Modell)**")
            st.json(step["result"])


st.title("💬 Chat-Agent")
st.caption(
    "Ein lokaler LLM-Agent (über Ollama) beantwortet Fragen und ruft dafür das "
    "Vorhersagemodell als **Tool** auf."
)

with st.sidebar:
    st.header("⚙️ Einstellungen")
    try:
        available = [m.model for m in ollama.list().models]
    except Exception:
        available = [DEFAULT_MODEL]
    default_idx = available.index(DEFAULT_MODEL) if DEFAULT_MODEL in available else 0
    model_name = st.selectbox("Ollama-Modell", available, index=default_idx)
    st.caption("Das Modell muss Tool-Calling unterstützen.")
    if st.button("🗑️ Verlauf löschen", use_container_width=True):
        st.session_state.chat = []
        st.rerun()

if "chat" not in st.session_state:
    st.session_state.chat = []

# Replay history.
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        render_tool_steps(msg.get("tool_steps", []))

# New input.
if prompt := st.chat_input("z. B.: Verdient ein 45-jähriger Manager mit 60 Wochenstunden über 50K?"):
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat]
    with st.chat_message("assistant"):
        try:
            with st.spinner("Agent denkt nach …"):
                answer, tool_steps = run_agent(history, model_name)
            if not answer.strip():
                answer = "_(Das Modell hat keine Textantwort geliefert — siehe Tool-Aufruf unten.)_"
        except Exception as exc:
            answer, tool_steps = (
                f"⚠️ Verbindung zu Ollama fehlgeschlagen: `{exc}`\n\n"
                "Läuft der Ollama-Server (`ollama serve`)? Und ist das gewählte "
                "Modell vorhanden (`ollama list`)?",
                [],
            )
        st.markdown(answer)
        render_tool_steps(tool_steps)

    st.session_state.chat.append(
        {"role": "assistant", "content": answer, "tool_steps": tool_steps}
    )
