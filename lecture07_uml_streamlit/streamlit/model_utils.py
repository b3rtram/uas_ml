"""Domain logic for the churn app.

This file is the code behind the Block 1 class diagram:

    BaseModel  <|--  ChurnModel        (inheritance)
    ChurnModel  *--  Preprocessor      (composition: the sklearn Pipeline owns its preprocessor)
    ChurnModel  ..>  DataLoader        (dependency: trained with data the loader provides)

The two cached functions at the bottom are the entry points the Streamlit
pages actually call. They demonstrate the cache_resource vs. cache_data split
from the lecture.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

import joblib
import pandas as pd
import streamlit as st

CSV_PATH = "churn.csv"
MODEL_PATH = "model.pkl"


class DataLoader:
    """Loads the churn dataset from disk. (DataLoader in the class diagram.)"""

    def __init__(self, path: str = CSV_PATH) -> None:
        self.path = path

    def load(self) -> pd.DataFrame:
        return pd.read_csv(self.path)


class BaseModel(ABC):
    """Abstract base — every model must be able to return a churn probability."""

    @abstractmethod
    def predict_proba(self, X: pd.DataFrame):
        ...


class ChurnModel(BaseModel):
    """Wraps a scikit-learn Pipeline.

    The Pipeline owns its preprocessor (a ColumnTransformer named "prep"),
    which is the composition arrow in the diagram.
    """

    def __init__(self, pipeline=None) -> None:
        self.pipeline = pipeline

    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        self.pipeline.fit(X, y)

    def predict_proba(self, X: pd.DataFrame):
        # Probability of class 1 (= churn) for each row.
        return self.pipeline.predict_proba(X)[:, 1]

    def save(self, path: str = MODEL_PATH) -> None:
        joblib.dump(self.pipeline, path)

    @classmethod
    def load(cls, path: str = MODEL_PATH) -> "ChurnModel":
        return cls(joblib.load(path))


# --- Cached entry points used by the Streamlit pages -------------------------

@st.cache_resource
def load_model() -> ChurnModel:
    """Loaded ONCE per server process, shared across reruns and sessions.

    A model is a resource, not data -> cache_resource (no copy on each call).
    """
    return ChurnModel.load()


@st.cache_data
def load_data() -> pd.DataFrame:
    """Cached as DATA -> returned as a fresh copy each call, cheap to reuse."""
    return DataLoader().load()
