"""REST API for the Auto MPG model. Start with:  python -m uvicorn api:app --port 8000"""
import json
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

MODEL_DIR = Path(__file__).parent / "models"
model = joblib.load(MODEL_DIR / "mpg_model.joblib")                     # load ONCE at start, not per request
meta = json.loads((MODEL_DIR / "mpg_model.json").read_text())

app = FastAPI(title="Auto MPG model")


class Car(BaseModel):                                                    # the input contract
    cylinders: int = Field(ge=3, le=12)
    displacement: float = Field(gt=0, description="cubic inches")
    horsepower: float | None = Field(default=None, gt=0)                 # may be missing: the pipeline imputes it
    weight: float = Field(gt=0, description="lb")
    acceleration: float = Field(gt=0, description="seconds 0-60 mph")
    model_year: int = Field(ge=70, le=82)
    origin: Literal["usa", "europe", "japan"]


class Prediction(BaseModel):                                             # the output contract
    mpg: float
    expected_error_mpg: float


@app.get("/health")
def health():
    return {"status": "ok", "trained_at": meta["trained_at"], "test_mae": meta["test_mae"]}


@app.post("/predict")
def predict(car: Car) -> Prediction:
    X = pd.DataFrame([car.model_dump()])                                 # JSON -> one-row DataFrame, like in training
    return Prediction(mpg=round(float(model.predict(X)[0]), 1),
                      expected_error_mpg=meta["test_mae"])
