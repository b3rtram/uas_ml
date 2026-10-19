"""Create the demo dataset and train the churn model.

Run once before the lecture:  python train_model.py
Produces:  churn.csv  and  model.pkl

The data is synthetic but has sensible structure: customers with short tenure,
high monthly charges, month-to-month contracts and fiber-optic internet churn
more often. This makes the dashboard's predictions feel realistic.
"""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from lecture07_uml_streamlit.streamlit.model_utils import CSV_PATH, MODEL_PATH, ChurnModel

rng = np.random.default_rng(42)
n = 2000

tenure = rng.integers(0, 73, n)
monthly = rng.uniform(20, 120, n).round(2)
contract = rng.choice(["Month-to-month", "One year", "Two year"], n, p=[0.55, 0.25, 0.20])
internet = rng.choice(["DSL", "Fiber optic", "No"], n, p=[0.35, 0.45, 0.20])

logit = (
    -0.5
    - 0.04 * tenure
    + 0.02 * (monthly - 70)
    + np.where(contract == "Month-to-month", 1.2, np.where(contract == "One year", 0.1, -0.8))
    + np.where(internet == "Fiber optic", 0.7, np.where(internet == "No", -0.5, 0.0))
)
prob = 1 / (1 + np.exp(-logit))
churn = (rng.uniform(0, 1, n) < prob).astype(int)

df = pd.DataFrame(
    {
        "tenure": tenure,
        "MonthlyCharges": monthly,
        "Contract": contract,
        "InternetService": internet,
        "Churn": churn,
    }
)
df.to_csv(CSV_PATH, index=False)

X = df.drop(columns="Churn")
y = df["Churn"]

numeric = ["tenure", "MonthlyCharges"]
categorical = ["Contract", "InternetService"]

# The ColumnTransformer is the "Preprocessor" the ChurnModel composes.
preprocessor = ColumnTransformer(
    [
        ("num", StandardScaler(), numeric),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
    ]
)
pipeline = Pipeline([("prep", preprocessor), ("clf", LogisticRegression(max_iter=1000))])

model = ChurnModel(pipeline)
model.train(X, y)
model.save(MODEL_PATH)

print(f"Saved {MODEL_PATH} and {CSV_PATH}")
print(f"Churn rate: {churn.mean():.1%}   Train accuracy: {pipeline.score(X, y):.1%}")
