"""ML SERVICE: only the model behind one REST endpoint. No web page, no database, no FMP key.
Start:  python -m uvicorn app:app --port 8001    (docs: http://127.0.0.1:8001/docs)"""
from fastapi import FastAPI
from pydantic import BaseModel, Field, PositiveFloat

import model

rf = model.load_model()                        # once at start, not per request
app = FastAPI(title="Stock App · ML service")


class Closes(BaseModel):                       # the contract: what a valid request looks like
    closes: list[PositiveFloat] = Field(min_length=model.LAGS + 1, description="prices, oldest first")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(body: Closes):
    return {"return_pct": model.predict_return(rf, body.closes)}
