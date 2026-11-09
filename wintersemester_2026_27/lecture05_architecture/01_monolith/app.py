"""PRESENTATION LAYER: delivers the web page and the REST endpoints.
Translates HTTP <-> Python and nothing else: no SQL, no model.
Start:  python -m uvicorn app:app --port 8000    then open http://127.0.0.1:8000"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

import logic

app = FastAPI(title="Stock App · monolith")


@app.get("/")
def page():
    return FileResponse(Path(__file__).parent / "index.html")


@app.post("/api/predict/{symbol}")
def predict(symbol: str):
    try:
        return logic.predict_tomorrow(symbol)
    except logic.UnknownSymbol:
        raise HTTPException(404, f"unknown symbol {symbol}")


@app.get("/api/predictions/{symbol}")
def predictions(symbol: str):
    return logic.history(symbol)
