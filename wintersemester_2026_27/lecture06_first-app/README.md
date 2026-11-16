# Session 6 · A first app

| folder | what | start |
|---|---|---|
| `01_streamlit_basics/` | Streamlit, one page per facet: text, widgets, data, charts, layout, status, rerun and state, caching, chat | `streamlit run app.py` |
| `02_react_basics/` | React, the same ideas in JavaScript: components, props, state, events, fetch, a backend call | `npm install`, `npm run dev` |
| `03_stock_app/` | **the whole chain** in Streamlit: FMP API → prices → chart → placeholder for your ML model | `streamlit run app.py` |

`01` and `02` run with made-up prices, no API key needed. `03` needs `FMP_API_KEY=...` in the `.env` file in the repo root.
`03` is the starting point for your own app: only `predict_next_close()` has to change.
