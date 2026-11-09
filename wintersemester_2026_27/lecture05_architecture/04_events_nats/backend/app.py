"""PRESENTATION LAYER of the backend: web page and REST endpoints for the browser.
Start (NATS must run, see README):
    python -m uvicorn app:app --port 8000    then open http://127.0.0.1:8000"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

import events
import logic


@asynccontextmanager
async def lifespan(app):                                   # runs once at start (before yield) and at stop (after)
    await events.connect()
    await events.subscribe("predictions.created", "backend", logic.on_prediction)
    yield
    await events.close()


app = FastAPI(title="Stock App · backend (events)", lifespan=lifespan)


@app.get("/")
def page():
    return FileResponse(Path(__file__).parent / "index.html")


@app.post("/api/predict/{symbol}", status_code=202)       # 202 Accepted: received, the result comes later
async def predict(symbol: str):
    try:
        return await logic.request_prediction(symbol)
    except logic.UnknownSymbol:
        raise HTTPException(404, f"unknown symbol {symbol}")


@app.get("/api/predictions/{symbol}")
def predictions(symbol: str):
    return logic.history(symbol)
