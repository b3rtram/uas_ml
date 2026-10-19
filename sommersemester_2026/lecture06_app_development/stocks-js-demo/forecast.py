"""
forecast.py — FORECASTING layer (the "ML" of this demo).

Trains a Prophet model on historical data and predicts N days into the future.
This is where your real ML model would live — swap Prophet for ARIMA, LSTM,
or whatever you want, and as long as you keep the function signature,
nothing else in the project needs to change.
"""

import logging

import pandas as pd
from prophet import Prophet

# Prophet via cmdstanpy is very chatty by default — quiet it down.
logging.getLogger("cmdstanpy").setLevel(logging.WARNING)
logging.getLogger("prophet").setLevel(logging.WARNING)


def make_forecast(history: pd.DataFrame, horizon_days: int) -> dict:
    """
    Train Prophet on `history`, predict `horizon_days` ahead, return both
    the historical and the future-only forecast points.
    """
    model = Prophet(
        daily_seasonality=False,
        weekly_seasonality=True,
        yearly_seasonality=True,
        interval_width=0.80,  # 80% confidence band
    )
    model.fit(history)

    future = model.make_future_dataframe(periods=horizon_days)
    forecast_df = model.predict(future)

    # Keep only the future portion — historical part is already in `history`
    last_hist_date = history["ds"].max()
    future_only = forecast_df[forecast_df["ds"] > last_hist_date]

    historical = [
        {"date": ts.strftime("%Y-%m-%d"), "value": float(val)}
        for ts, val in zip(history["ds"], history["y"])
    ]
    forecast = [
        {
            "date": row["ds"].strftime("%Y-%m-%d"),
            "yhat": float(row["yhat"]),
            "yhat_lower": float(row["yhat_lower"]),
            "yhat_upper": float(row["yhat_upper"]),
        }
        for _, row in future_only.iterrows()
    ]

    return {
        "historical": historical,
        "forecast": forecast,
        "latest_price": float(history["y"].iloc[-1]),
    }
