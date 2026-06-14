"""Income-prediction agent (Ollama) — UI-independent.

Shared by the Streamlit chat page and the Discord bot. Contains the tool
definition, the system prompt and the agent loop. No Streamlit, no Discord —
just plain Python so it can run anywhere.

Tool-shape note: smaller local models (e.g. Gemma) reliably emit a tool call
only when the function has a *single* parameter. We therefore expose one
``features_json`` string argument (a JSON object of feature:value pairs) instead
of 12 separate arguments.
"""

import json

import ollama

from model_service import get_schema, predict_income

DEFAULT_MODEL = "gemma4:latest"

_schema = get_schema()

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
            f"Valid feature names (use exactly these): {', '.join(_schema['feature_columns'])}.\n"
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
    valid = set(_schema["feature_columns"])
    normalized = {}
    for key, value in data.items():
        if key not in valid and key.replace("_", "-") in valid:
            key = key.replace("_", "-")
        normalized[key] = value

    return predict_income(**normalized)


TOOLS = {"predict_income": call_predict_income}


def run_agent(history: list[dict], model: str = DEFAULT_MODEL, max_steps: int = 5):
    """Run one agent turn: chat -> (tool calls -> chat)* -> final answer.

    ``history`` is a list of {"role": "user"|"assistant", "content": str}.
    Returns ``(final_text, tool_steps)`` where tool_steps is a list of
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
