# Stock Price Predictor

Frankfurt UAS · Machine Learning · Lecture 5
**Linear Regression vom Notebook zur App**

Dieses Repo enthält eine minimal lauffähige Stock-App, die ein Linear-Regression-Modell auf Aktienkurse trainiert und es in einer Streamlit-App benutzt.

---

## Quickstart

### 1. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 2. Modell trainieren

```bash
python train.py
```

Das erzeugt `model.pkl` — das ist das gelernte Modell (~600 Bytes).

### 3. App starten

```bash
streamlit run app.py
```

Browser öffnet sich automatisch mit der App.

---

## Was macht was?

| Datei | Zweck |
|---|---|
| `train.py` | Lädt AAPL-Daten von Yahoo Finance, trainiert Linear Regression, speichert das Modell in `model.pkl`. Läuft selten. |
| `app.py` | Streamlit-App. Lädt `model.pkl`, holt aktuelle Kursdaten, zeigt Chart + Prediction. Läuft oft. |
| `requirements.txt` | Python-Dependencies. |
| `.gitignore` | Was nicht ins Git-Repo gehört (inkl. `*.pkl`, weil das Modell aus `train.py` regenerierbar ist). |

---

## Modell-Architektur

Linear Regression mit drei Features:

- `Close` — heutiger Schlusskurs
- `Volume` — heutiges Handelsvolumen
- `MA7` — 7-Tage Moving Average des Close

**Target:** Schlusskurs am nächsten Handelstag.

Modell-Gleichung:

```
Tomorrow_Close = w₁·Close + w₂·Volume + w₃·MA7 + b
```

`fit()` lernt die vier Zahlen `w₁`, `w₂`, `w₃`, `b`.

---

## Hausaufgaben

1. **Pflicht:** App auf einen anderen Ticker (MSFT, NVDA, ...) zeigen lassen. Liefert das mit AAPL trainierte Modell sinnvolle Predictions? Was beobachtet ihr?
2. **Empfohlen:** `train.py` so umbauen, dass der Ticker als Argument übergeben wird (`python train.py --ticker MSFT`). App so erweitern, dass sie das passende Modell zum gewählten Ticker lädt.
3. **Bonus:** Slider in der App für "Tage in die Zukunft". Hinweis: das Modell predicted nur einen Tag voraus — die Lücke zu sehen ist Teil der Aufgabe.
