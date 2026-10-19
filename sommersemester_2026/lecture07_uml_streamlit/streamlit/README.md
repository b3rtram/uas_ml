# Streamlit Deep Dive — Lecture 7 demo

Companion code for **Lecture 7: From Diagram to Interface**. It builds the app
that the Block 1 UML diagrams describe: a multipage Streamlit app with a churn
**dashboard** and an Ollama-powered **agent** chat.

## Setup

```bash
pip install -r requirements.txt
python train_model.py        # creates churn.csv and model.pkl
streamlit run streamlit_app.py
```

For the agent page, also install and start Ollama:

```bash
ollama pull gemma4
ollama serve
```

If Ollama is not running, the agent page falls back to a fake stream, so the
app still runs in class.

## File map (and where it shows up in the lecture)

| File | Block | What it shows |
|------|-------|---------------|
| `counter_broken.py` | 2 | The rerun model — a counter that forgets |
| `counter_fixed.py` | 3 | The fix — `st.session_state` |
| `model_utils.py` | 1, 4 | The class diagram in code + `cache_resource` / `cache_data` |
| `train_model.py` | — | Builds `churn.csv` and `model.pkl` (run once) |
| `streamlit_app.py` | 5 | Multipage entry with `st.navigation` |
| `views/dashboard.py` | 5 | Sidebar inputs, `st.columns`, `st.tabs`, chart, dataframe |
| `views/agent.py` | 6 | `st.chat_message`, `st.chat_input`, `st.write_stream`, Ollama |

## How the code mirrors the UML

`model_utils.py` is the Block 1 class diagram in code:

- `BaseModel` is abstract; `ChurnModel` inherits from it (`<|--`).
- `ChurnModel` owns its preprocessor through the sklearn Pipeline (`*--`).
- `ChurnModel` depends on `DataLoader` for training data (`..>`).

The app structure (`streamlit_app.py` + the two pages + shared `model_utils`)
is the Block 1 component diagram.
