# Lecture 2 — How does Machine Learning work?

Kompletter Durchstich an einem echten Beispiel: *Schließt AAPL morgen höher als heute?*

Daten laden (FMP API) → Daten anschauen → Features & Target → zeitlicher Train/Test-Split
→ Baseline → Random Forest → ehrliche Evaluation (inkl. Overfitting) → Prognose für morgen.

## Setup

1. Kostenlosen API-Key holen: <https://financialmodelingprep.com>
2. Im Repo-Root eine `.env` anlegen:
   ```
   FMP_API_KEY=dein_key
   ```
3. Notebook `lecture02_ml_pipeline.ipynb` öffnen und von oben nach unten ausführen.

Benötigt: `pandas`, `scikit-learn`, `matplotlib`, `requests`, `python-dotenv`.

## Dateien

| Datei | Inhalt |
|---|---|
| `lecture02_ml_pipeline.ipynb` | Das Notebook für die Vorlesung |
| `fmp_data.py` | Lädt Tagespreise von FMP und cached die rohe JSON-Antwort in `data/<SYMBOL>.json` |

Zum Neuladen der Daten einfach `data/AAPL.json` löschen (oder `load_prices("AAPL", refresh=True)`).
