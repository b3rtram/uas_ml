"""PRESENTATION LAYER of the backend: the web page and the REST endpoints for the browser.
Start (the ML service should run on port 8001):
    python -m uvicorn app:app --port 8000    then open http://127.0.0.1:8000"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

import logic

app = FastAPI(title="Stock App · backend")


@app.get("/")
def page():
    return FileResponse(Path(__file__).parent / "index.html")


@app.post("/api/predict/{symbol}")
def predict(symbol: str):
    try:
        return logic.predict_tomorrow(symbol)
    except logic.UnknownSymbol:
        raise HTTPException(404, f"unknown symbol {symbol}")
    except logic.ModelUnavailable:                         # new: the other service can be down
        raise HTTPException(503, "ML service not reachable, try again later")


@app.get("/api/predictions/{symbol}")
def predictions(symbol: str):
    return logic.history(symbol)
