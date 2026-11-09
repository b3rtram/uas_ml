"""BUSINESS LAYER of the backend. Against 02: the REST call to the ML service is gone.
Instead the backend publishes 'prices.updated' and later receives 'predictions.created'."""
import asyncio
from datetime import datetime, timezone

import data
import events

LAGS = 10                                                  # the ML service needs LAGS + 1 prices


class UnknownSymbol(Exception):
    pass


async def request_prediction(symbol):
    symbol = symbol.upper()
    prices = await asyncio.to_thread(data.fetch_prices, symbol)    # FMP call in a thread: the server stays responsive
    if len(prices) < LAGS + 1:
        raise UnknownSymbol(symbol)
    data.save_prices(symbol, prices)

    closes = [p["close"] for p in prices]
    queued_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")   # same format as SQLite datetime('now')
    await events.publish("prices.updated", {"symbol": symbol, "as_of": prices[-1]["date"],
                                            "closes": closes[-(LAGS + 1):]})
    return {"status": "queued", "symbol": symbol, "as_of": prices[-1]["date"],
            "queued_at": queued_at, "last_prices": prices[-10:]}  # no prediction yet: it comes later


async def on_prediction(event):
    """Called for every 'predictions.created' event from the ML service."""
    close, return_pct = event["close"], event["return_pct"]
    data.save_prediction({"symbol": event["symbol"], "as_of": event["as_of"], "close": close,
                          "return_pct": round(return_pct, 3),
                          "close_next": round(close * (1 + return_pct / 100), 2)})
    print(f"saved prediction for {event['symbol']}: {return_pct:+.3f} %", flush=True)


def history(symbol):
    return data.get_predictions(symbol.upper())
