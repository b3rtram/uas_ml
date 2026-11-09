# Session 5 · Software architecture: from a monolith to two services

The Stock App gets a web page and a backend. We build it twice:

| folder | architecture | programs that run |
|---|---|---|
| `01_monolith/` | one program, inside it three layers | 1 (port 8000) |
| `02_two_services/` | the model moves into its own service | 2 (ports 8000 and 8001) |
| `04_events_nats/` | the two services talk via events over NATS instead of REST | 2 + the NATS server |

Needs `FMP_API_KEY=...` in the `.env` file in the repo root (as in Session 2).

## 01 · Monolith

```
browser: index.html  ── POST /api/predict/AAPL ──▶  ONE PROGRAM (port 8000)
                     ◀── JSON ─────────────────────  app.py    presentation layer: page + REST endpoints
                                                     logic.py  business layer: features + model
                                                     data.py   data layer: FMP + SQLite (stock.db)
```

```bash
cd 01_monolith
python train.py                                   # once: creates models/stock_rf.joblib
python -m uvicorn app:app --port 8000             # start
```
Open http://127.0.0.1:8000 (or http://127.0.0.1:8000/?symbol=MSFT). API docs: http://127.0.0.1:8000/docs

**The layer rule:** each layer only calls the layer below it. `app.py` never writes SQL, `data.py` never sees HTTP.

## 02 · Two services

```
browser ──REST──▶ backend (port 8000)            ──REST──▶ ml_service (port 8001)
                  app.py, logic.py, data.py                 app.py, model.py
                  web page, FMP, SQLite                     only the model
```

```bash
cd 02_two_services/ml_service
python train.py                                   # once
python -m uvicorn app:app --port 8001             # terminal 1

cd 02_two_services/backend
python -m uvicorn app:app --port 8000             # terminal 2
```

Compared with the monolith, only `backend/logic.py` changed: `load_model().predict(X)` became `requests.post(".../predict")`.
`index.html` and `data.py` are identical. Stop the ML service and press Predict: the page shows **503**.

## 04 · Event-based with NATS

```
browser ─POST─▶ backend ── event "prices.updated" ──────▶ NATS ──▶ ml_service   (no HTTP, no port)
        ◀─202──         ◀─ event "predictions.created" ── NATS ◀──
page asks GET /api/predictions every 0.5 s until the prediction is there
```

The backend doesn't call the ML service and doesn't wait for it. It publishes an event and answers **202 Accepted**.
NATS **JetStream** stores every event, so nothing is lost while a service is down.

```bash
docker run -d --name nats -p 4222:4222 -p 8222:8222 nats:2.10 -js -m 8222   # the NATS server (once)
pip install nats-py

cd 04_events_nats/ml_service
python train.py                                   # once
python service.py                                 # terminal 1

cd 04_events_nats/backend
python -m uvicorn app:app --port 8000             # terminal 2
```
Without Docker: download `nats-server` from https://nats.io/download and run `nats-server -js -m 8222`.
Watch the stream and its consumers: http://127.0.0.1:8222/jsz?consumers=true

Compared with `02`: `index.html` waits for the result (polling), `logic.py` publishes instead of calling, and the new
`events.py` (same file in both services) does the NATS work. `data.py` and `model.py` are unchanged.
Things to try:
- Stop `service.py`, press Predict: the page says "waiting", the event waits in NATS. Start `service.py` again: the prediction appears.
- Start `service.py` twice: both share the events (same group `ml_service`), each event is processed once.

## Exercises

1. **Required:** stop the ML service in `02_two_services` and press Predict. What does the browser show, what is in `stock.db`, and why?
2. **Recommended:** add `GET /api/prices/{symbol}` to the monolith. Which of the three files do you have to touch? (Answer: all three, one function each.)
3. **Bonus:** replace SQLite with a CSV file. Which files change in `01_monolith`? Which in `02_two_services`?
4. **Events:** add an `alert_service.py` in `04_events_nats` that listens to `predictions.created` (own group `alerts`) and prints a line for every prediction above +0.3 %. Which existing file do you have to change? (Answer: none.)
