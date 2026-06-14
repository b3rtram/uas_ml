# Stock Forecast — JavaScript Frontend + Python Backend + SQLite

**Demo 1 of 2.** A stock-price forecaster where everything is wired up by hand: HTML/CSS/JS in the browser, FastAPI on the server, SQLite for the portfolio, and explicit HTTP between them. Show this first, then Demo 2 (Streamlit) for the contrast.

## What it does

- Add stock tickers to a portfolio (AAPL, MSFT, SAP.DE, TSLA, …)
- The portfolio persists in SQLite across server restarts
- Click any ticker to fetch its data from Yahoo Finance and run a 30-day Prophet forecast
- The chart shows historical prices, the forecast line, and the 80% confidence band

## Project structure

```
stocks-js-demo/
├── requirements.txt
├── server.py            ← BACKEND  — FastAPI routes (orchestrator)
├── data.py              ← BACKEND  — yfinance wrapper
├── forecast.py          ← BACKEND  — Prophet model
├── db.py                ← DATABASE — SQLite portfolio
└── public/
    ├── index.html       ← FRONTEND — HTML structure
    ├── style.css        ← FRONTEND — CSS appearance
    └── app.js           ← FRONTEND — JavaScript behavior + Chart.js
```

Seven code files. Three languages on the frontend, one on the backend, SQL in the database. This is the architectural diagram from the lecture, made literal in the file tree.

## Setup

You need Python 3.10+ and an internet connection (yfinance reaches Yahoo).

```bash
# Install dependencies. Prophet's first install pulls cmdstanpy and may
# take a minute or two on the first run.
pip install -r requirements.txt

# Start the server
uvicorn server:app --reload
```

Open <http://localhost:8000>.

## REST API

| Method | Endpoint                          | What it does                        |
|--------|-----------------------------------|-------------------------------------|
| GET    | `/api/portfolio`                  | List portfolio                      |
| POST   | `/api/portfolio`                  | Add a ticker                        |
| DELETE | `/api/portfolio/{id}`             | Remove a ticker                     |
| GET    | `/api/forecast/{ticker}?horizon=30` | Fetch + forecast for one ticker     |

Also: <http://localhost:8000/docs> for the interactive Swagger UI.

### Quick curl test

```bash
# Add a stock
curl -X POST http://localhost:8000/api/portfolio \
  -H "Content-Type: application/json" \
  -d '{"ticker": "AAPL"}'

# List portfolio
curl http://localhost:8000/api/portfolio

# Run a forecast
curl "http://localhost:8000/api/forecast/AAPL?horizon=30"
```

## What to point out in class

Open `public/app.js` and walk through the wiring that **you** had to write by hand:

1. **`async function apiListPortfolio()` and the other api calls** — every interaction with the backend is a `fetch()`. You construct the URL, set the method, serialize the body to JSON, parse the response. Four such functions for four endpoints.

2. **`addForm.addEventListener("submit", …)`** — you intercept the submit event and call `event.preventDefault()` so the page doesn't reload. Same for the delegated click handler on the portfolio list.

3. **`renderPortfolio()` rebuilds the `<ul>` manually** — `innerHTML = ""`, then `document.createElement("li")`, then `appendChild()` in a loop. Every visible change to the page is an explicit DOM mutation.

4. **The whole `drawChart()` function** — destroy the previous chart, build datasets, configure axes, set colors, hide cosmetic series from the legend. None of this would exist if we were using Streamlit, which renders the chart from a single `st.line_chart(...)` call.

5. **State management is manual** — `currentChart` lives at module scope so we can `.destroy()` it before redrawing. Streamlit handles state for you via reruns.

Each of those five points becomes one or two lines in the Streamlit version.

## A few useful tickers for the demo

- `AAPL`, `MSFT`, `GOOGL`, `TSLA` — well-known US stocks
- `SAP.DE`, `BMW.DE`, `DTE.DE` — German tickers (.DE suffix for Xetra)
- `^GDAXI` — DAX index, `^GSPC` — S&P 500
- `BTC-USD`, `ETH-USD` — crypto pairs

A fun classroom comparison: a stable blue chip (`MSFT`) vs. a volatile one (`TSLA`) over 30 days. Prophet's confidence band gets dramatically wider on the volatile one — visible proof that the model knows what it doesn't know.

## What's deliberately not in here

- No authentication
- No caching of historical data — every forecast re-fetches from Yahoo
- No async for yfinance/Prophet (both are synchronous; fine for a single-user demo)
- No tests
- No production deployment configuration

This is a teaching scaffold, not production code.
