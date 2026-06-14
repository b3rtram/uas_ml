# Architektur — Lecture 09 Deployment

Komponentendiagramm der Anwendung (GitHub rendert Mermaid automatisch).

```mermaid
flowchart TB
    user([👤 Nutzer:in])

    subgraph streamlit["🖥️ Streamlit-App (app.py · st.navigation)"]
        form["form_page.py<br/><i>Seite 1 – Formular</i>"]
        chat["chat_page.py<br/><i>Seite 2 – Chat-UI</i>"]
    end

    subgraph discordcomp["🤖 Discord-Bot"]
        bot["discord_bot.py<br/><i>Gateway-Client</i>"]
    end

    subgraph core["⚙️ Geteilter Kern"]
        agent["agent.py<br/><i>run_agent · TOOL_SPEC · Prompt</i>"]
        svc["model_service.py<br/><i>load_artifact · get_schema · predict_income</i>"]
    end

    model[("📦 adult_income_model.joblib<br/><i>Pipeline + Metadaten</i>")]
    nb["📓 eda_adult.ipynb<br/><i>Training</i>"]

    ollama{{"🦙 Ollama-Server<br/>gemma4 (Tool-Calling)"}}
    gateway{{"💬 Discord Gateway"}}
    env[/".env<br/>DISCORD_BOT_TOKEN"/]

    %% Nutzerzugänge
    user -->|"Browser"| streamlit
    user -->|"DM / @mention"| gateway

    %% Training -> Artefakt
    nb -->|"trainiert &amp; speichert"| model

    %% UI -> Kern
    form -->|"predict_income()"| svc
    chat -->|"run_agent()"| agent
    bot  -->|"run_agent()"| agent

    %% Kern intern / extern
    agent -->|"predict_income() (Tool)"| svc
    agent -->|"get_schema() → Tool-Schema"| svc
    agent -->|"ollama.chat(tools=…)"| ollama
    svc  -->|"lädt"| model

    %% Bot-Anbindung
    bot <-->|"WebSocket (ausgehend)"| gateway
    env -.->|"Token"| bot

    classDef external fill:#fde68a,stroke:#b45309,color:#000;
    classDef artifact fill:#bfdbfe,stroke:#1e40af,color:#000;
    class ollama,gateway,env external;
    class model,nb artifact;
```

## Kernideen

- **`agent.py` + `model_service.py`** bilden den geteilten Kern — von der
  Streamlit-Chat-Seite **und** vom Discord-Bot wiederverwendet.
- Das **Formular** ruft das Modell **direkt** auf (`predict_income`), während
  **Chat und Bot** über den **Agenten** gehen, der das Modell als **Tool**
  aufruft.
- **gemma4 (Ollama)** und der **Discord-Gateway** sind externe Systeme; der
  Bot verbindet sich **ausgehend** (kein offener Port nötig).
- Das **Modell-Artefakt** wird vom Notebook erzeugt und ausschließlich von
  `model_service` geladen.

## Ablauf einer Chat-Anfrage (Tool-Calling)

```mermaid
sequenceDiagram
    autonumber
    actor U as Nutzer:in
    participant UI as Chat-UI / Discord-Bot
    participant AG as agent.run_agent
    participant OL as Ollama (gemma4)
    participant MS as model_service.predict_income
    participant M as Modell-Pipeline (joblib)

    U->>UI: Frage ("45, Manager, 60 Std/Woche?")
    UI->>AG: run_agent(history)
    AG->>OL: chat(messages, tools=[predict_income])
    OL-->>AG: tool_call predict_income(features_json)

    AG->>MS: predict_income(**features)
    MS->>M: predict_proba(X)
    M-->>MS: P(>50K)
    MS-->>AG: {prediction, probability}

    AG->>OL: chat(messages + tool-Ergebnis)
    OL-->>AG: finale Antwort (Text)
    AG-->>UI: (answer, tool_steps)
    UI-->>U: Antwort + Wahrscheinlichkeit
```

## Mermaid-Quelldateien

Die rohen Diagrammquellen liegen unter [`diagrams/`](diagrams/) und lassen sich
mit jedem Mermaid-Renderer zu Bildern exportieren:

- [`diagrams/component.mmd`](diagrams/component.mmd) — Komponentendiagramm
- [`diagrams/sequence_chat.mmd`](diagrams/sequence_chat.mmd) — Sequenzdiagramm

```bash
# Beispiel: PNG/SVG erzeugen (Node nötig)
npx -p @mermaid-js/mermaid-cli mmdc -i diagrams/component.mmd -o component.svg
```
