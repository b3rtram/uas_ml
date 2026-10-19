# Stock Forecast — Streamlit all-in-one

**Demo 2 of 2.** Same app as Demo 1, but everything fits in one Python file.

## What it does

The same as Demo 1: add tickers to a portfolio (persists in SQLite), click a ticker to fetch its history from Yahoo Finance, see a 30-day Prophet forecast with confidence band. Identical features, identical behavior.

## Project structure

```
stocks-streamlit-demo/
├── requirements.txt
└── app.py               ← everything
```

One file. The database, the data layer, the forecast logic, and the UI all live inside `app.py`. Compare to Demo 1's seven files spread across three languages.

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

Streamlit prints a URL — usually <http://localhost:8501>. That's it. No separate backend to start.

## The side-by-side comparison

Open `app.py` and Demo 1's files in two editor windows. Walk through these matchups in front of the class:

| Demo 1 (JS frontend + Python backend)                                | Demo 2 (Streamlit)                              |
|----------------------------------------------------------------------|-------------------------------------------------|
| `<form id="add-form">` in `index.html`                               | `with st.form("add-form"):`                     |
| `addForm.addEventListener("submit", ...)` in `app.js`                | `if submitted:`                                 |
| `await fetch("/api/portfolio", {method: "POST", body: JSON…})`       | `add_to_portfolio(new_ticker)` — direct call   |
| `renderPortfolio()` — innerHTML, createElement, appendChild loop    | `for item in portfolio: cols = st.columns(...)` |
| `await fetch("/api/forecast/" + ticker)`                             | `make_forecast(history, 30)` — direct call     |
| `drawChart()` — destroy old chart, build datasets, configure axes    | `st.plotly_chart(fig, use_container_width=True)`|
| `currentChart` module-level variable for chart state                 | `st.session_state["selected"]`                  |
| The fact that `uvicorn` runs the API and Streamlit would be separate | Streamlit IS the web server                     |

Every row collapses several lines of manual wiring into a Streamlit primitive.

## What's the same as Demo 1

The pieces that **don't** depend on the frontend/backend split are identical between the two demos:

- Same SQLite schema (`portfolio` table with id, ticker, added_at)
- Same yfinance call to get historical prices
- Same Prophet setup (weekly + yearly seasonality, 80% confidence interval)
- Same business logic in every other respect

That's deliberate: the contrast you see is **purely** the architectural cost of separating frontend from backend. If you keep them together (Streamlit), the architecture gets simpler. If you split them (Demo 1), you gain flexibility — multiple frontends, GPU offloading for ML, etc. — but you pay for it in wiring.

## When to pick which

- **Streamlit** when you're building a tool for a known audience (your colleagues, your customers in a small SaaS, an internal dashboard, a research demo). One developer. Fast iteration.
- **Separated stack** when you need multiple frontends (web + mobile + dashboard), independent scaling of compute-heavy ML versus light business logic, a different team owning each layer, or any kind of public API for third parties.

Streamlit isn't strictly better or worse — it's the right tool when the constraints of "everything is Python and runs in one process" don't bite. The moment they do, you go to Demo 1's architecture.

## The pedagogical line

> "Streamlit is great when you want speed. The trade-off is that you give up control. Today you've seen what's underneath — and now you can choose."
