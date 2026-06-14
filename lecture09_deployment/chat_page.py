"""Page 2 — chat agent (Ollama) that calls the model through a tool.

The agent is a local LLM served by Ollama. It is given a single tool,
``predict_income``, wired to the exact same model as page 1. The agent decides
on its own when it has enough information, calls the tool, and explains the
result in natural language.

Note on the tool shape: smaller local models (e.g. Gemma) reliably emit a tool
call only when the function has a *single* parameter. We therefore expose one
``features_json`` string argument (a JSON object of feature:value pairs) instead
of 12 separate arguments. This is a common, robust pattern for local tool use.
"""

import json

import ollama
import streamlit as st

from model_service import get_schema, predict_income

schema = get_schema()


# --- Tool definition ---------------------------------------------------------
EXAMPLE = '{"age": 50, "occupation": "Exec-managerial", "hours-per-week": 60, "education-num": 14}'

TOOL_SPEC = {
    "type": "function",
    "function": {
        "name": "predict_income",
        "description": (
            "Predict whether a person earns more than $50K/year using the trained "
            "Adult/Census-Income model. Provide a JSON object string of "
            "feature:value pairs. Any field may be omitted; missing values are "
            "imputed automatically. Returns the predicted label and the "
            "probability of >50K.\n"
            f"Valid feature names (use exactly these): {', '.join(schema['feature_columns'])}.\n"
            f"Example: {EXAMPLE}"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "features_json": {
                    "type": "string",
                    "description": (
                        "A JSON object of feature:value pairs using the exact "
                        f"feature names listed above. Example: {EXAMPLE}"
                    ),
                }
            },
            "required": ["features_json"],
        },
    },
}

SYSTEM_PROMPT = (
    "Du bist ein freundlicher Assistent, der einschätzt, ob eine Person mehr als "
    "50.000 $ im Jahr verdient. Rufe dafür IMMER das Tool `predict_income` auf — "
    "rate niemals selbst. Übergib die aus dem Gespräch bekannten Merkmale (Alter, "
    "Beruf, Wochenstunden, Bildungsjahre, Familienstand usw.) als JSON-Objekt. "
    "Fehlende Angaben darfst du weglassen (sie werden automatisch ergänzt) — frage "
    "nicht nach optionalen Feldern wie sex, race oder native-country. Erkläre das "
    "Ergebnis anschließend verständlich und nenne die Wahrscheinlichkeit. Antworte "
    "auf Deutsch."
)


def call_predict_income(features_json: str = "{}") -> dict:
    """Tool implementation: parse the JSON argument and run the model."""
    try:
        data = json.loads(features_json) if isinstance(features_json, str) else dict(features_json)
    except (json.JSONDecodeError, TypeError) as exc:
        return {"error": f"could not parse features_json: {exc}"}

    # Be lenient about underscore vs. hyphen (e.g. hours_per_week -> hours-per-week).
    valid = set(schema["feature_columns"])
    normalized = {}
    for key, value in data.items():
        if key not in valid and key.replace("_", "-") in valid:
            key = key.replace("_", "-")
        normalized[key] = value

    return predict_income(**normalized)


TOOLS = {"predict_income": call_predict_income}


# --- Agent loop --------------------------------------------------------------
def run_agent(history: list[dict], model: str, max_steps: int = 5):
    """Run one agent turn: chat -> (tool calls -> chat)* -> final answer.

    Returns (final_text, tool_steps) where tool_steps is a list of
    {tool, args, result} dicts for transparent display.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, *history]
    tool_steps = []

    for _ in range(max_steps):
        response = ollama.chat(model=model, messages=messages, tools=[TOOL_SPEC])
        message = response["message"]
        messages.append(message)

        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            return message.get("content") or "", tool_steps

        for call in tool_calls:
            name = call["function"]["name"]
            args = dict(call["function"]["arguments"] or {})
            func = TOOLS.get(name)
            result = func(**args) if func else {"error": f"unknown tool: {name}"}
            tool_steps.append({"tool": name, "args": args, "result": result})
            messages.append({"role": "tool", "content": json.dumps(result)})

    return (
        "Ich habe zu viele Tool-Aufrufe gebraucht und stoppe hier. "
        "Bitte formuliere die Anfrage etwas konkreter.",
        tool_steps,
    )


# --- UI ----------------------------------------------------------------------
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
        available = ["gemma4:latest"]
    default_idx = available.index("gemma4:latest") if "gemma4:latest" in available else 0
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
