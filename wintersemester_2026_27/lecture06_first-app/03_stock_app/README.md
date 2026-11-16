# Stock App (Streamlit)

The whole chain in one file: **FMP API → prices → chart → ML placeholder**.
Use it as the starting point for your own app.

```bash
pip install -r requirements.txt
streamlit run app.py              # opens http://localhost:8501   (or http://localhost:8501/?symbol=MSFT)
```
Needs `FMP_API_KEY=...` in the `.env` file in the repo root (as in Session 2).

`app.py` has the three layers from Session 5, top to bottom:

| layer | function | what it does |
|---|---|---|
| data | `fetch_prices(symbol, days)` | FMP request, cached for one hour |
| logic | `predict_next_close(prices)` | **placeholder for your model**: today it returns "tomorrow = today" |
| presentation | the rest of the file | sidebar, metrics, chart, prediction box, table, download |

## Put your model in

Only `predict_next_close()` changes. Its docstring shows the RandomForest from Session 4/5 as an example.
Load the model with `@st.cache_resource`, otherwise it is loaded again after every click.
