"""ML SERVICE as an event consumer: no web server, no port, no URL.
It listens to 'prices.updated' and answers with 'predictions.created'.
Start (NATS must run):  python service.py"""
import asyncio

import events
import model

rf = model.load_model()                                    # once at start


async def on_prices(event):
    return_pct = model.predict_return(rf, event["closes"])
    await events.publish("predictions.created", {"symbol": event["symbol"], "as_of": event["as_of"],
                                                 "close": event["closes"][-1], "return_pct": return_pct})
    print(f"{event['symbol']}: {return_pct:+.3f} %", flush=True)


async def main():
    await events.connect()
    await events.subscribe("prices.updated", "ml_service", on_prices)
    print("ML service: waiting for events on prices.updated", flush=True)
    await asyncio.Event().wait()                           # wait forever; NATS calls on_prices in the background


if __name__ == "__main__":
    asyncio.run(main())
