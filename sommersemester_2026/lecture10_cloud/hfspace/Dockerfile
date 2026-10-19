# Hugging Face Space (Docker SDK) — Variante B: das fertige Image aus GHCR ziehen.
#
# Der Space baut hier NICHTS aus dem Quellcode. Er zieht nur das Image, das der
# GitHub-Actions-Workflow nach GHCR gepusht hat, und startet es. Alle Settings
# (CMD, ENABLE_CHAT=0, PORT=8080, EXPOSE) werden vom Base-Image geerbt.
#
# Voraussetzung: das GHCR-Package muss PUBLIC sein, sonst kann HF es nicht ziehen.
FROM ghcr.io/b3rtram/income-predictor:latest

# HF Spaces startet den Container ggf. als Nicht-root-User. HOME auf ein
# beschreibbares Verzeichnis legen, damit Streamlit seine Config anlegen kann.
ENV HOME=/tmp
