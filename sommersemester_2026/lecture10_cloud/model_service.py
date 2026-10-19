"""Model service for the Adult / Census Income deployment.

This module is deliberately free of any Streamlit code so it can be reused
everywhere: by the form page, by the chat agent's tool, and from a plain
Python script or test. Everything is driven by the saved artifact produced in
``eda_adult.ipynb`` — load it once, then ask it what it needs.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import logging as log

import joblib
import numpy as np
import pandas as pd

MODEL_PATH = Path(__file__).parent / "models" / "adult_income_model.joblib"


@lru_cache(maxsize=1)
def load_artifact() -> dict:
    """Load the persisted model artifact (cached for the process lifetime)."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. Run eda_adult.ipynb first to "
            "train and save the model."
        )
    return joblib.load(MODEL_PATH)


@lru_cache(maxsize=1)
def get_schema() -> dict:
    """Derive the input schema directly from the fitted pipeline.

    Returns the numerical/categorical column lists, a sensible default per
    numerical column (the median learned by the imputer) and the allowed
    levels per categorical column (the categories learned by the encoder).
    Form widgets and the agent's tool description both read from here, so they
    can never drift out of sync with the model.
    """
    art = load_artifact()
    column_transformer = art["model"].steps[0][1]
    transformers = {name: t for name, t, cols in column_transformer.transformers_}

    num_medians = transformers["num"].named_steps["imputer"].statistics_
    cat_categories = transformers["cat"].named_steps["ohe"].categories_

    return {
        "feature_columns": list(art["feature_columns"]),
        "num_cols": list(art["num_cols"]),
        "cat_cols": list(art["cat_cols"]),
        "num_defaults": {
            c: float(m) for c, m in zip(art["num_cols"], num_medians)
        },
        "cat_options": {
            c: [str(x) for x in cats]
            for c, cats in zip(art["cat_cols"], cat_categories)
        },
        "classes": art["classes"],
    }


def predict_income(**features) -> dict:
    """Predict whether a person earns >50K from raw feature values.

    Any column may be omitted or left as ``None`` — the pipeline imputes it
    (median for numbers, most-frequent for categories). Unknown categorical
    levels are ignored safely by the one-hot encoder. This is exactly the
    function the chat agent calls as a tool.
    """
    art = load_artifact()
    schema = get_schema()
    cols = schema["feature_columns"]

    row = {c: features.get(c) for c in cols}
    X = pd.DataFrame([row], columns=cols)

    # Enforce dtypes the pipeline expects: numbers as float (missing -> NaN),
    # categoricals as plain objects.
    for c in schema["num_cols"]:
        X[c] = pd.to_numeric(X[c], errors="coerce")
    for c in schema["cat_cols"]:
        X[c] = X[c].astype("object").where(X[c].notna(), np.nan)

    model = art["model"]
    proba = float(model.predict_proba(X)[0][1])
    label = art["classes"][1] if proba >= 0.5 else art["classes"][0]

    return {
        "prediction": label,
        "probability_over_50k": round(proba, 4),
        "used_features": {k: v for k, v in row.items() if v not in (None, "")},
    }
