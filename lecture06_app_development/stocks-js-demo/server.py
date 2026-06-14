"""
server.py — BACKEND.

A FastAPI server that:
  1. Serves the static frontend files from /public on the root path
  2. Exposes REST endpoints for portfolio management and forecasting

The backend orchestrates three modules — none of which know about each other:
    data.py     — fetches stock prices from yfinance
    forecast.py — runs Prophet
    db.py       — persists the portfolio to SQLite

Run with:
    uvicorn server:app --reload
"""

import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import data
import db
import forecast as forecast_module


app = FastAPI(title="Stock Forecast Demo — JS frontend")


# ---------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------

class AddStockInput(BaseModel):
    ticker: str = Field(min_length=1, max_length=20)


# ---------------------------------------------------------------
# Portfolio endpoints — CRUD on the user's watchlist
# ---------------------------------------------------------------

@app.get("/api/portfolio")
def list_portfolio() -> list[dict]:
    """Return all tickers currently in the portfolio."""
    return db.list_portfolio()


@app.post("/api/portfolio")
def add_stock(payload: AddStockInput) -> dict:
    """Add a ticker to the portfolio."""
    try:
        return db.add_to_portfolio(payload.ticker)
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail=f"'{payload.ticker.upper()}' is already in the portfolio",
        )


@app.delete("/api/portfolio/{stock_id}")
def remove_stock(stock_id: int) -> dict:
    """Remove a ticker from the portfolio."""
    if not db.delete_from_portfolio(stock_id):
        raise HTTPException(status_code=404, detail="not found")
    return {"ok": True}


# ---------------------------------------------------------------
# Forecast endpoint — the ML pipeline
# ---------------------------------------------------------------

@app.get("/api/forecast/{ticker}")
def get_forecast(ticker: str, horizon: int = 30, history: int = 365) -> dict:
    """
    Fetch historical data for `ticker`, run Prophet, return the forecast.
    The DB is not involved in this call — forecasts are computed on demand
    and not cached. (Caching would be a perfectly reasonable extension.)
    """
    if horizon < 1 or horizon > 180:
        raise HTTPException(status_code=400, detail="horizon must be 1..180 days")
    if history < 30 or history > 3650:
        raise HTTPException(status_code=400, detail="history must be 30..3650 days")

    # 1) Fetch data
    try:
        history_df = data.fetch_stock_history(ticker.upper(), history)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to fetch data from Yahoo Finance: {e}",
        )

    # 2) Run the model
    result = forecast_module.make_forecast(history_df, horizon)

    # 3) Return everything the frontend needs to render
    return {
        "ticker": ticker.upper(),
        "horizon_days": horizon,
        "history_days": history,
        **result,
    }


# ---------------------------------------------------------------
# Serve the frontend (HTML, CSS, JS) on /
# Mount LAST so the /api routes above take precedence.
# ---------------------------------------------------------------

app.mount("/", StaticFiles(directory="public", html=True), name="public")
