# Lecture 09 — Model Deployment

Fortführung von Lecture 08 (`eda_adult.ipynb`): Wir trainieren das beste Modell,
speichern es und stellen es in einer **Streamlit-App mit zwei Seiten** bereit.

> 📐 Architekturüberblick (Komponentendiagramm): siehe [ARCHITECTURE.md](ARCHITECTURE.md).

## Inhalt

| Datei | Zweck |
|---|---|
| `eda_adult.ipynb` | EDA + Modellvergleich aus Lecture 08, **plus** Abschnitte 16–18: bestes Modell auf allen Daten refitten und als `joblib` speichern. |
| `models/adult_income_model.joblib` | Gespeichertes Artefakt: vollständige Pipeline (Preprocessing + Gradient Boosting) inkl. Metadaten. |
| `model_service.py` | Modell-Logik ohne Streamlit: Laden, Schema aus der Pipeline ableiten, `predict_income()`. Wird überall genutzt. |
| `agent.py` | LLM-Agent ohne UI: Tool-Definition, System-Prompt, Agent-Loop (`run_agent`). Von Chat-Seite **und** Discord-Bot genutzt. |
| `app.py` | Einstiegspunkt, verdrahtet die beiden Seiten via `st.navigation`. |
| `form_page.py` | **Seite 1** — Formular, das die Merkmale einer Person abfragt und das Modell direkt aufruft. |
| `chat_page.py` | **Seite 2** — Chat mit einem lokalen LLM-Agenten (Ollama), der das Modell als **Tool** (`predict_income`) aufruft. |
| `discord_bot.py` | Bonus: derselbe Agent als **Discord-Bot** (Gateway, läuft lokal — keine öffentliche URL nötig). |

## Starten

```bash
# 1. Modell erzeugen (falls models/adult_income_model.joblib noch fehlt):
jupyter nbconvert --to notebook --inplace --execute eda_adult.ipynb

# 2. Für Seite 2: Ollama-Server + ein tool-fähiges Modell
ollama serve            # in einem eigenen Terminal
ollama pull gemma4      # oder ein anderes Modell mit Tool-Calling

# 3. App starten
streamlit run app.py
```

Seite 1 funktioniert ohne Ollama. Seite 2 braucht einen laufenden Ollama-Server.

### Discord-Bot (optional)

```bash
# Voraussetzung: Bot im Discord Developer Portal angelegt,
# MESSAGE CONTENT INTENT aktiviert, Token in ../.env als DISCORD_BOT_TOKEN.
ollama serve            # in einem eigenen Terminal
python discord_bot.py
```

Der Bot verbindet sich **ausgehend** zu Discord (Gateway), läuft also lokal
hinter dem Router ohne offenen Port. Antwortet in DMs direkt und in Server-
Kanälen, wenn man ihn @erwähnt. Hinweis: Ein Discord-**Webhook** kann nur
senden, nicht empfangen — zum Empfangen braucht es einen Bot wie hier.

## Hinweis zum Tool-Design (Seite 2)

Kleinere lokale Modelle (z. B. Gemma) erzeugen nur dann zuverlässig einen
Tool-Aufruf, wenn die Funktion **einen einzigen Parameter** hat. Das Tool
`predict_income` nimmt deshalb ein einzelnes `features_json` (ein JSON-Objekt
aus `feature:value`-Paaren) statt 12 Einzelargumente entgegen. Fehlende Felder
werden von der Pipeline automatisch imputiert.
