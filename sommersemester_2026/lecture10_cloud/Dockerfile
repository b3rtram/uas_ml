# Container image for the cloud-ready Income Predictor (Lecture 10).
#
# Why a Dockerfile in addition to the Procfile? A Procfile lets a Heroku-style
# buildpack guess everything for you. A Dockerfile makes the environment
# *explicit and reproducible* — same image locally, in CI and in the cloud.
# Many PaaS platforms deploy a Dockerfile directly if one is present.

# Slim Python base — matches .python-version. Small image, no GPU, no Ollama.
FROM python:3.12-slim

# Predictable Python behaviour in containers:
#   no .pyc files, unbuffered stdout/stderr so logs show up immediately.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies FIRST, in their own layer. As long as requirements.txt
# is unchanged, Docker reuses this cached layer and skips re-installing on every
# code change. We install only the cloud deps (no ollama).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the application code (changes often -> kept after the deps layer).
COPY . .

# Cloud config: no Ollama here, so run the form page only. $PORT is injected by
# the platform at runtime; default to 8080 for plain `docker run`.
ENV ENABLE_CHAT=0 \
    PORT=8080
EXPOSE 8080

# Shell form so $PORT is expanded at runtime. Bind to 0.0.0.0 and run headless.
CMD streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true
