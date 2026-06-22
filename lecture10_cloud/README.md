# Lecture 10 — Cloud-Deployment (PaaS)

Fortführung von Lecture 09: Dort lief die App **lokal** (Streamlit-Formular +
Ollama-Chat-Agent + Discord-Bot). Jetzt bringen wir dieselbe App in die
**Cloud** auf eine **PaaS** (Platform-as-a-Service, Heroku-Style — z. B.
itdone3) und bekommen eine **öffentliche HTTPS-URL**.

> 📐 Lokal-vs-Cloud-Überblick + Deployment-Diagramm: siehe
> [ARCHITECTURE.md](ARCHITECTURE.md).

## Lernziele

- Verstehen, was eine **PaaS** automatisch übernimmt (Build, Container, TLS,
  Routing, öffentliche URL) — und was *du* liefern musst.
- Eine App **cloud-fähig** machen: an `$PORT` binden, Start über ein
  **`Procfile`**, Dependencies in **`requirements.txt`**, Konfiguration über
  **Umgebungsvariablen/Secrets**.
- Begreifen, **warum nicht alles deploybar ist**: Der lokale Ollama-LLM braucht
  ein mehrere GB großes Modell und idealerweise eine GPU — beides hat ein
  schlanker PaaS-Container nicht. Lokales ≠ Cloud.

## Inhalt

| Datei | Zweck |
|---|---|
| `app.py` | Einstiegspunkt. **Neu ggü. L09:** Chat-Seite nur, wenn `ENABLE_CHAT=1` (Default lokal). In der Cloud `ENABLE_CHAT=0` → **nur Formular**. |
| `form_page.py` | Formular-Seite (unverändert aus L09). Ruft das Modell direkt auf — **braucht keinen LLM**, läuft überall. |
| `model_service.py` | Modell-Logik ohne Streamlit (unverändert). Lädt das `joblib`-Artefakt. |
| `chat_page.py`, `agent.py` | Chat-Agent (Ollama). **Nur lokal** sinnvoll, in der Cloud nicht aktiv. |
| `models/adult_income_model.joblib` | Trainiertes Pipeline-Artefakt aus L08/L09. Wird **mit deployt** (liegt im Repo). |
| `Procfile` | Sagt der PaaS, wie der `web`-Prozess startet (bindet an `$PORT`). |
| `Dockerfile` | Alternative zum Buildpack: **explizites, reproduzierbares** Image. |
| `.dockerignore` | Hält den Build-Kontext / das Image klein. |
| `requirements.txt` | **Cloud**-Dependencies (Versionen gepinnt auf den Trainingsstand). |
| `requirements-local.txt` | Extra `ollama` — nur für die lokale Chat-Seite. |
| `.python-version` | Welche Python-Version der Buildpack nehmen soll. |
| `.streamlit/config.toml` | Streamlit-Einstellungen hinter einem Reverse-Proxy. |

## Lokal starten

```bash
# Voller Umfang lokal (Formular + Chat):
pip install -r requirements.txt -r requirements-local.txt
ollama serve            # eigenes Terminal (für die Chat-Seite)
ollama pull gemma4      # tool-fähiges Modell
streamlit run app.py    # ENABLE_CHAT ist standardmäßig an

# Nur das, was später in der Cloud läuft, lokal nachstellen:
ENABLE_CHAT=0 streamlit run app.py
```

## In die Cloud deployen (itdone3, Heroku-Style)

Das eigentliche Deployment macht ihr selbst — als reproduzierbare Übung. Die
Schritte sind bei jeder Heroku-artigen PaaS gleich:

### 1. Was die Plattform für dich tut
- erkennt am `requirements.txt` automatisch, dass es eine **Python-App** ist
  (Buildpack),
- baut daraus einen **Container**,
- vergibt eine **Default-Domain** `https://<service>-<app-slug>.endofweb.de`,
- terminiert **TLS** und routet eingehende Requests an deinen `$PORT`.

### 2. Was du lieferst
- **`Procfile`** mit dem Startbefehl (siehe unten),
- **`requirements.txt`** mit allen Dependencies,
- die App muss auf **`$PORT`** und **`0.0.0.0`** lauschen.

Unser `Procfile`:

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

### 3. Schritte

1. **App anlegen** und mit dem Git-Repo verknüpfen (URL deines Repos).
2. **Service** hinzufügen, der auf den Pfad `lecture10_cloud/` zeigt
   (Buildpack erkennt Python automatisch).
3. **Secret/ENV setzen:** `ENABLE_CHAT=0` (sonst versucht die App, die
   Chat-Seite anzubieten, die ohne Ollama nicht funktioniert).
4. **Build & Deploy** auslösen.
5. Die **öffentliche URL** öffnen → `https://<service>-<app-slug>.endofweb.de`.
6. Bei Fehlern: **Build- und Runtime-Logs** ansehen.

> Tipp: Genau diese Schritte lassen sich auch über die itdone3-Tools
> automatisieren (App anlegen, Service hinzufügen, Secrets setzen, deployen,
> Logs holen). Für die Vorlesung machen wir sie bewusst **von Hand**, damit
> klar wird, *was* dabei passiert.

## Alternative: per Docker deployen

Statt den Buildpack raten zu lassen, kann man die Umgebung mit einem
**`Dockerfile`** explizit festlegen — gleiches Image lokal, in CI und in der
Cloud. Viele PaaS deployen ein vorhandenes Dockerfile direkt.

```bash
# Image bauen
docker build -t income-predictor lecture10_cloud

# Lokal starten (Cloud-Verhalten: nur Formular, gebunden an Port 8080)
docker run --rm -p 8080:8080 income-predictor
# → http://localhost:8080

# Anderen Port simulieren (wie eine PaaS via $PORT)
docker run --rm -e PORT=9000 -p 9000:9000 income-predictor
```

`Procfile` (Buildpack) **oder** `Dockerfile` — beide tun dasselbe: die App an
`$PORT` binden und headless starten. Du brauchst nur einen Weg; das Dockerfile
ist der explizitere.

## CI/CD mit GitHub Actions

Der Workflow liegt im Repo-Root unter
[`.github/workflows/deploy-lecture10.yml`](../.github/workflows/deploy-lecture10.yml)
(GitHub findet Workflows nur dort) und greift nur bei Änderungen an
`lecture10_cloud/**`. Zwei Jobs:

1. **`test`** — installiert die Cloud-Dependencies, ruft das Modell einmal auf
   (`predict_income`) und startet die App headless, um den Health-Endpoint
   `/_stcore/health` zu prüfen. Schlägt das fehl, wird nichts gebaut.
2. **`build-push`** — baut das Docker-Image und pusht es in die **GitHub
   Container Registry**: `ghcr.io/<owner>/income-predictor` (Tags `latest`
   und `sha-<commit>`). Läuft nur bei echten Pushes, nicht bei Pull Requests.

```
push to main ─▶ test ─▶ build-push ─▶ ghcr.io/<owner>/income-predictor ─▶ PaaS zieht das Image
```

Die PaaS deployt dann nicht mehr aus dem Quellcode, sondern **zieht das fertige
Image** aus GHCR. Damit das geht:

- **Package öffentlich machen** (GitHub → Packages → *income-predictor* →
  *Package settings* → Visibility *public*), **oder**
- der PaaS Registry-Credentials hinterlegen (GHCR-Pull mit einem Token).

> `secrets.GITHUB_TOKEN` reicht zum **Pushen** aus dem Workflow heraus — dafür
> braucht es kein zusätzliches Secret, nur die `packages: write`-Permission
> (steht im Workflow). Externe Secrets bräuchtest du erst, wenn der Workflow
> selbst die PaaS-API anspräche.

## Warum läuft der Chat-Agent nicht in der Cloud?

Der Agent aus L09 spricht mit einem **lokalen Ollama-Server**. Dieser:

- lädt ein **mehrere GB großes** Sprachmodell auf die Maschine,
- läuft sinnvoll nur **mit GPU**,
- ist ein **separater Dienst**, der mitlaufen muss.

Ein schlanker PaaS-Container bringt davon nichts mit. Man könnte den Agenten
**cloud-fähig** machen, indem man Ollama durch eine **gehostete LLM-API**
(mit Tool-Calling) ersetzt und den API-Key als Secret hinterlegt — das ist aber
ein eigenes Thema. Hier zeigen wir deshalb in der Cloud nur die Formular-Seite
(`ENABLE_CHAT=0`) und behalten den Chat **lokal**.

## Troubleshooting

| Symptom | Ursache / Lösung |
|---|---|
| App startet, aber „Anwendung antwortet nicht" | Nicht an `$PORT` gebunden → Startbefehl im `Procfile` prüfen. |
| `ModuleNotFoundError: ollama` in den Logs | `ENABLE_CHAT` nicht auf `0` → Cloud lädt die Chat-Seite. Secret setzen. |
| sklearn-Warnung beim Laden des Modells | Version in `requirements.txt` weicht vom Trainingsstand ab → Pins angleichen. |
| Weiße Seite / WebSocket-Fehler | Reverse-Proxy: `enableCORS=false` + `enableXsrfProtection=false` (in `.streamlit/config.toml`). |
