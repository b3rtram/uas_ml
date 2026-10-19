# Fine-Tuning in klein — Sentiment mit Mini-BERT

Das **einfachste mögliche Fine-Tuning-Beispiel**, nur um den Gedanken zu zeigen:
Ein vortrainiertes Sprachmodell (`distilbert-base-uncased`) wird mit **16 Sätzen**
in **10 Epochen** (Sekunden) darauf nachtrainiert, Sätze als *positiv* / *negativ*
einzusortieren.

**Der Aha-Moment im Notebook:**

| | Testsätze (neu, nie im Training) |
|---|---|
| **vorher** (nur geladen) | rät alles gleich (p ≈ 0.5) |
| **nachher** (fine-getunt) | alle korrekt, p ≈ 0.7–0.9 |

## Ausführen

```bash
cd lecture11_finetune
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python torch transformers ipykernel jupyter
.venv/bin/jupyter lab finetune_sentiment.ipynb
```

> Eigenes Python-3.12-venv, weil das Haupt-Repo auf 3.14 läuft (wo `transformers`
> nicht sauber installiert).

## Modell

Das Notebook lädt aus `models/distilbert-base-uncased/` falls vorhanden, sonst
direkt von Hugging Face. Hängt der Hub-Download, lädt man `model.safetensors`
(~268 MB) robust per parallelen Range-Requests (siehe `lecture11_security`/
TimesFM-README für das curl-Snippet).

## Dateien

| Datei | Zweck |
|-------|-------|
| `finetune_sentiment.ipynb` | Beispiel 1 — **Classification-Kopf**: Text → positiv/negativ |
| `finetune_qa.ipynb` | Beispiel 2 — **QuestionAnswering-Kopf**: Frage + Text → Antwort-Stelle |
| `models/distilbert-base-uncased/` | lokale Modellkopie (nicht eingecheckt) |

Beide Notebooks nutzen **denselben Körper** (`distilbert-base-uncased`) mit einem
**anderen Kopf** — und beide folgen demselben Bogen: laden → *vorher* (Kopf rät) →
Fine-Tuning → *nachher* (Aufgabe gelöst). Das ist der rote Faden: **Körper =
allgemeines Können, Kopf = konkrete Aufgabe, Fine-Tuning = der Nachschliff.**

## Der Gedanke (für die Tafel)

1. **Vortrainiert** = das Modell kann schon grob Sprache.
2. **Fine-Tuning** = kurzer Nachschliff auf *deinen* paar Beispielen.
3. Gleiches Prinzip wie bei großen Foundation-Modellen (GPT, BERT, Bild-/
   Zeitreihenmodelle) — nur dass „groß" mehr Daten/Rechenzeit und Tricks wie
   LoRA braucht.
