# Streamlit basics

A tour through Streamlit: each page shows one facet. The full Stock App is in `../03_stock_app`.
Every page is one short file in `pages/`. Open the file next to the browser and change things.

```bash
pip install -r requirements.txt
streamlit run app.py              # opens http://localhost:8501
```

All pages use made-up prices (`demo_data.py`) and run without internet and without an API key.

| page | file | what you see |
|---|---|---|
| Text | `01_text.py` | title, markdown, LaTeX, code, `st.write`, magic |
| Widgets | `02_widgets.py` | 17 input widgets and the value each one returns |
| Data | `03_data.py` | metric, dataframe with column config, data editor, table, JSON, download |
| Charts | `04_charts.py` | line, area, bar, scatter, map; Altair, Plotly, Matplotlib |
| Layout | `05_layout.py` | sidebar, columns, tabs, expander, container, popover, dialog, empty |
| Status | `06_status.py` | success/info/warning/error, spinner, progress, status, toast, balloons |
| Rerun and state | `07_rerun_state.py` | **the key idea**: rerun, session state, callbacks, forms, fragments, query params |
| Caching | `08_cache.py` | `@st.cache_data` vs. `@st.cache_resource`, with timings |
| Chat | `09_chat.py` | chat messages, chat input, streaming text |

## The one idea to remember

Every click runs the **whole file again, from top to bottom**. That is why
- a normal variable forgets (`count = 0` again every run) → use `st.session_state`,
- slow work (download, training) must be cached → `@st.cache_data`, `@st.cache_resource`.

Compare with Session 5: there the browser (`index.html`) and the backend (`app.py`) were two programs talking REST.
With Streamlit **one Python file is both**: Streamlit builds the web page from your Python code.

## Exercises

1. **Required:** on page 7, click "+1 (normal variable)" three times. Why does `count` never go above 1?
2. **Recommended:** on page 8, remove `@st.cache_data` from `load_prices()` and switch symbols. What happens, and why?
3. **Bonus:** on page 9, let the bot answer 'chart AAPL' with a `st.line_chart` inside the assistant message.
