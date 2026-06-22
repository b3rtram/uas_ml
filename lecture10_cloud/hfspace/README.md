---
title: Income Predictor
emoji: 💼
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8080
pinned: false
---

# Income Predictor — Hugging Face Space

Docker-Space, der das in GitHub Actions gebaute Image aus der GitHub Container
Registry zieht (`ghcr.io/b3rtram/income-predictor`). Quellcode und Lehrmaterial:
[uas_ml / lecture10_cloud](https://github.com/b3rtram/uas_ml/tree/main/lecture10_cloud).

Gezeigt wird nur die **Formular-Seite** (`ENABLE_CHAT=0`) — der lokale
Ollama-Chat aus Lecture 09 läuft auf einer GPU-losen Cloud-Instanz nicht.

> **`app_port: 8080`** muss zu dem Port passen, auf dem der Container lauscht.
> Unser Image lauscht per Default auf `8080` (`ENV PORT=8080`).
