# Surface 1 — Die Webapp: OWASP Top 10 (2025)

*Erklär-Notizen zum Selbstlesen. Bezug: die Stock-App (Streamlit auf Hugging Face Spaces, FMP-API, RandomForest/TimesFM). Code-Beispiele sind im `Security_Code_Examples.ipynb`.*

## Was die OWASP Top 10 überhaupt sind

Die zehn **folgenreichsten Risiko-Kategorien** für Webanwendungen — nicht „die zehn häufigsten". Das Ranking gewichtet drei Dinge: Verbreitung (wie oft kommt es vor), Ausnutzbarkeit (wie leicht angreifbar) und Auswirkung (wie groß der Schaden). Acht Plätze kommen aus Messdaten (>175.000 ausgewertete Schwachstellen-Records), zwei werden bewusst per Community-Umfrage gesetzt — für Risiken, die Praktiker als wichtig einstufen, auch wenn sie in den Daten noch selten auftauchen.

Es ist ein **Awareness-Dokument**, kein vollständiger Standard. Es geht um *Kategorien* von Risiken, nicht um einzelne Bugs.

**Neu in der 2025er-Fassung** (veröffentlicht 6. November 2025): zwei neue Kategorien — A03 Software Supply Chain Failures und A10 Mishandling of Exceptional Conditions; SSRF ist als eigene Kategorie verschwunden und in A01 aufgegangen; Security Misconfiguration ist auf Platz 2 hochgesprungen.

Ein roter Faden, der durch fast alles läuft: **Eine Lücke entsteht, wenn nicht-vertrauenswürdige Daten in einen Kontext geraten, der sie als Befehl liest.** Bei XSS ist dieser Kontext der Browser, bei SQLi die Datenbank, bei Supply-Chain der Interpreter. Wenn du das einmal verinnerlicht hast, hängen sich die Einzelfälle von selbst dran.

---

## A01 · Broken Access Control (inkl. SSRF)

**Was es ist.** Autorisierung — *was darf jemand tun?* — schlägt fehl. Ein Nutzer greift auf etwas zu, das ihm nicht zusteht: die Daten anderer Nutzer, Admin-Funktionen, fremde Logs. Seit 2025 gehört auch **SSRF** (Server-Side Request Forgery) hierher.

**Warum es ein Problem ist.** Es ist die Kategorie mit den meisten realen Vorfällen. „Eingeloggt sein" heißt nicht „alles dürfen" — wenn die App nicht bei *jeder* Anfrage serverseitig prüft, ob dieser Nutzer genau diese Ressource sehen darf, kann jeder durch Raten von IDs die Daten anderer abrufen.

**SSRF konkret bei der Stock-App.** Deine App holt serverseitig Kursdaten von der FMP-API. Bei SSRF bringt ein Angreifer deinen Server dazu, eine Anfrage an ein *Ziel seiner Wahl* zu schicken. Dein Server steht im internen Netz und genießt Vertrauen, das ein Außenstehender nicht hat — er kann interne Dienste oder den Cloud-Metadaten-Dienst (`http://169.254.169.254/...`, liefert oft Zugangs-Tokens) erreichen, an die der Angreifer selbst nicht herankommt.

**Der Fix.** Niemals Host oder URL vom Nutzer bestimmen lassen. Host fest verdrahten, nur das eine harmlose Feld (den Ticker) zulassen und streng validieren:

```python
ALLOWED_HOST = "financialmodelingprep.com"
url = f"https://{ALLOWED_HOST}/stable/historical-price-eod/full"
requests.get(url, params={"symbol": ticker, "apikey": api_key}, timeout=10)
```

> **Merksatz:** A01 = „Darf dieser Nutzer das?" Serverseitig bei *jeder* Anfrage prüfen — und den Server nie eine URL abrufen lassen, deren Ziel der Nutzer bestimmt.

---

## A02 · Security Misconfiguration

**Was es ist.** Die Software ist okay, aber *falsch eingestellt*: Debug-Modus an, ausführliche Fehlerseiten, Default-Passwörter, zu offene CORS-Regeln, exponierte Admin-Endpunkte, Secrets im Klartext in der Konfiguration.

**Warum es ein Problem ist.** Auf Platz 2 hochgesprungen, weil es so allgegenwärtig ist — und weil es dem Angreifer oft den ersten Tritt verschafft: Eine Fehlerseite mit Stacktrace verrät interne Pfade, Bibliotheksversionen, manchmal Keys. Das ist Aufklärung frei Haus.

**Bezug zur Stock-App.** Auf HF Spaces: Liegen Secrets als Environment-Variable/`st.secrets` (richtig) oder hartkodiert im Repo (falsch)? Ist Debug-Output abgeschaltet? Werden bei einem Fehler Interna an den Nutzer durchgereicht?

**Der Fix.** Sichere Defaults, Debug aus, generische Fehlermeldungen nach außen, Secrets über die Plattform-Mechanik statt im Code, regelmäßig prüfen, was unbeabsichtigt erreichbar ist.

> **Merksatz:** Nicht der Code ist hier das Problem, sondern die Einstellungen drumherum. Default heißt nicht sicher.

---

## A03 · Software Supply Chain Failures *(neu 2025)*

**Was es ist.** Das Risiko kommt von *außen* — über das, was du in dein Projekt hereinziehst: Bibliotheken (Dependencies), Basis-Images, vortrainierte Modelle, Datensätze. Du vertraust fremdem Material und führst es aus.

**Warum es ein Problem ist.** Niedrige Prävalenz in den Messdaten, aber bewusst auf Platz 3 gesetzt, weil Auswirkung und Ausnutzbarkeit enorm sind und Scanner es schlecht erkennen. Eine einzige kompromittierte Abhängigkeit landet in tausenden Projekten gleichzeitig.

**Bezug zur Stock-App.** Jedes `pip install`, jedes Basis-Image, jedes von Hugging Face geladene Modell ist Lieferkette. Der eindrücklichste Fall: das `.pkl`-Modell (siehe A08) — eine Modelldatei von einem Fremden ist ausführbarer Code, nicht „nur Daten".

**Der Fix.** Dependencies pinnen, Herkunft und Hashes prüfen, eine Stückliste (SBOM) führen, Modelle als safetensors statt Pickle laden, fremde Pickles mit `picklescan`/`modelscan` scannen.

> **Merksatz:** Das Risiko sitzt nicht in deinem Code, sondern in dem, was du beziehst. „Vertraue ich der Quelle?"

---

## A04 · Cryptographic Failures

**Was es ist.** Sensible Daten werden nicht oder schlecht verschlüsselt: Übertragung ohne TLS, schwache/veraltete Algorithmen, Secrets im Klartext, selbstgebaute Krypto.

**Warum es ein Problem ist.** Wer den Datenverkehr oder die Datenbank abgreift, liest alles im Klartext mit — inklusive API-Keys und personenbezogener Daten (Brücke zur DSGVO).

**Bezug zur Stock-App.** Läuft alles über HTTPS? Wo liegt der FMP-Key, und wie? Werden geloggte Daten geschützt?

**Der Fix.** TLS überall, etablierte Bibliotheken statt Eigenbau, Keys über `st.secrets`/Env, niemals Geheimnisse im Klartext speichern oder loggen.

> **Merksatz:** Verschlüsselung ist kein Add-on. Daten im Transit *und* im Ruhezustand schützen, und nie selbst kryptografieren.

---

## A05 · Injection

**Was es ist.** Eingaben aus dem Browser sind erstmal nur Text. Gefährlich werden sie, wenn dieser Text irgendwo landet, wo er als *Anweisung* interpretiert wird. Zwei Geschmacksrichtungen am Ticker-Feld:

**XSS (Cross-Site Scripting) — der HTML-Kontext.** Baust du die Eingabe ins gerenderte HTML ein und der Browser interpretiert sie:
```python
st.markdown(f"<h3>Signal for {ticker}</h3>", unsafe_allow_html=True)
```
Eingabe `<script>alert(1)</script>` → der Browser *führt das Skript aus*. Hier harmlos ein Popup, in echt Cookie-Diebstahl. Fix: `unsafe_allow_html` weglassen — Streamlit escaped dann automatisch (`<script>` wird als Text angezeigt, nicht ausgeführt).

**SQLi (SQL Injection) — der Datenbank-Kontext.** Baust du eine Abfrage per String-Zusammenkleben:
```python
query = f"SELECT * FROM signals WHERE ticker = '{ticker}'"
```
Eingabe `x' OR '1'='1` → die Abfrage gibt *alle* Zeilen zurück, weil die Eingabe die *Struktur* der Abfrage verändert. Fix: parametrisierte Abfrage, die Daten und Befehl trennt:
```python
con.execute("SELECT * FROM signals WHERE ticker = ?", (ticker,))
```

**Warum es ein Problem ist.** Daten und Code vermischen sich. Der Angreifer schreibt Code, wo du nur Daten erwartet hast.

> **Merksatz:** Daten und Befehl trennen — escapen fürs HTML, parametrisieren für SQL. Niemals Strings zusammenkleben.

---

## A06 · Insecure Design

**Was es ist.** Die Lücke sitzt nicht in der Umsetzung, sondern im *Entwurf*: Es wurde nie durchdacht, was schiefgehen kann. Fehlendes Threat-Modeling, kein Rate-Limiting eingeplant, keine Missbrauchsfälle bedacht.

**Warum es ein Problem ist.** Sicheres Implementieren hilft nichts, wenn das Konzept selbst unsicher ist — das lässt sich nicht „wegpatchen", nur neu entwerfen. Deshalb hat dieser Punkt auch kein knappes Code-Beispiel: Es ist eine Denk-, keine Code-Lücke.

**Bezug zur Stock-App.** Hast du dir vor dem Bauen überlegt, wie das Signal-Feature missbraucht werden könnte? Was passiert bei einer Flut von Anfragen? Wer darf welche Daten sehen?

**Der Fix.** Threat-Modeling *vor* dem Coden: Welche Akteure, welche Missbrauchsfälle, welche Schutzmaßnahmen gehören ins Design.

> **Merksatz:** Manche Sicherheit muss man entwerfen, nicht implementieren. Erst denken, was schiefgehen kann.

---

## A07 · Authentication Failures

**Was es ist.** Authentifizierung — *wer bist du?* — schlägt fehl: schwache Passwörter zugelassen, kein Brute-Force-Schutz, Sessions ohne Ablauf, schlecht gespeicherte oder unsicher verglichene Credentials.

**Warum es ein Problem ist (am Beispiel API-Key-Prüfung).** Zwei subtile Fallen:

*Timing-Seitenkanal.* Der naive `==`-Vergleich bricht ab, sobald das erste Zeichen nicht passt — minimal schneller als wenn die ersten Zeichen stimmen. Diese Zeitunterschiede sind messbar; ein Angreifer knackt den Key *Zeichen für Zeichen* statt alles zu raten. Fix: konstant-zeitiger Vergleich:
```python
import hmac
hmac.compare_digest(provided, expected)   # braucht immer gleich lang
```
*Klartext-Speicherung.* Liegt der echte Key im Klartext, hat ihn jeder, der DB/Log/Backup abgreift. Fix: nur einen **Hash** des Keys speichern und den niemals loggen.

**Abgrenzung zu A01.** A07 = „Bist du, wer du behauptest?" (Authentifizierung). A01 = „Darfst du das?" (Autorisierung). Beides muss stimmen.

> **Merksatz:** Geheimnisse konstant-zeitig vergleichen, nur als Hash speichern, Anmeldeversuche begrenzen.

---

## A08 · Software or Data Integrity Failures

**Was es ist.** Du verlässt dich auf Code oder Daten, ohne zu prüfen, ob sie *unverändert* sind: unsignierte Updates, ungeprüfte Deserialisierung, manipulierte Artefakte.

**Warum es ein Problem ist — der Pickle-Fall.** Eine Pickle-Datei ist nicht nur Daten, sie ist ausführbarer Code. Beim Laden ruft pickle die Methode `__reduce__` auf, und was die zurückgibt, *wird ausgeführt* — vor jeder Nutzung:
```python
class Tampered:
    def __reduce__(self):
        return (print, ("arbitrary code ran at load time",))  # harmlos; könnte os.system sein
pickle.load(open("model.pkl", "rb"))   # hier läuft der Code
```
Das gilt auch für **joblib** — es nutzt pickle intern, erbt also die Lücke vollständig. joblib ist *nicht* die sichere Alternative, nur die bequemere.

**Der Fix (gestaffelt).** Neuronale Netze (TimesFM) als **safetensors** speichern — reines Tensor-Format, kein Code-Pfad. sklearn-Modelle musst du picklen → nur eigene Dateien laden und per **Hash** prüfen, dass sie unverändert sind. Fremde Pickles mit `picklescan` scannen, statt sie blind zu laden.

**Abgrenzung zu A03.** A03 = „Vertraue ich der *Quelle*?" A08 = „Wurde das Artefakt *unterwegs verändert*?" Das `.pkl` trifft beide.

> **Merksatz:** Eine Modelldatei von jemand anderem ist untrusted code. Code-freie Formate bevorzugen, sonst nur Eigenes mit Hash-Prüfung laden.

---

## A09 · Security Logging & Alerting Failures

**Was es ist.** Zu wenig Protokollierung, um einen Angriff zu erkennen oder nachzuvollziehen — oder Logs, die selbst zum Problem werden, weil Secrets/PII drinstehen. „Alerting" ist 2025 dazugekommen: Loggen allein reicht nicht, es muss auch jemand (oder etwas) bei Verdacht Alarm schlagen.

**Warum es ein Problem ist.** Ohne brauchbare Logs merkt man Einbrüche oft monatelang nicht. Und ein Log voller API-Keys ist ein zweites Datenleck.

**Bezug zur Stock-App.** Du loggst ohnehin für Drift-Monitoring (MLOps-Vorlesung). Schreibst du dabei versehentlich den API-Key aus dem Query-String mit? Würdest du merken, wenn *ein* Nutzer systematisch zehntausende Vorhersagen abruft (Brücke zu Model Extraction)?

**Der Fix.** Das Ereignis loggen, nicht die Geheimnisse — Keys/PII redigieren oder hashen. Und auf auffällige Muster alarmieren.
```python
logger.info("predict ticker=%s user=%s", ticker, user_id_hash)   # Event, kein Secret
```

> **Merksatz:** Logge das Ereignis, nicht das Geheimnis — und sorge dafür, dass jemand bei Missbrauch wach wird.

---

## A10 · Mishandling of Exceptional Conditions *(neu 2025)*

**Was es ist.** Fehlerfälle werden schlecht behandelt: unbehandelte Ausnahmen, Fehlerseiten mit Interna, „fail open" (im Fehlerfall den Zugriff erlauben statt verweigern), Race Conditions.

**Warum es ein Problem ist.** Ein leckender Stacktrace verrät interne Pfade und Versionen. Schlimmer: Wenn eine Prüfung im Fehlerfall *durchwinkt* statt zu blockieren, hebelt ein gezielt provozierter Fehler die Sicherheit aus.

**Bezug zur Stock-App.** Fängt dein FMP-Aufruf Fehler sauber ab, oder zeigt `st.write(e)` dem Nutzer den Stacktrace (samt evtl. Key)?

**Der Fix.** „Fail closed", volle Details nur serverseitig loggen, nach außen generische Meldungen:
```python
try:
    data = fetch_eod(ticker, FMP_API_KEY)
except Exception:
    logger.exception("fetch failed")          # Details intern
    st.error("Could not load data right now.") # generisch nach außen
```

> **Merksatz:** Im Fehlerfall sicher scheitern (fail closed) und nichts Internes nach außen leaken.

---

### Der gemeinsame Faden

Fast jede dieser Kategorien ist im Kern dieselbe Geschichte: *nicht-vertrauenswürdige Daten geraten in einen Kontext, der sie als Befehl/Zugriff/Ressource liest.* Die Abwehr rhymt überall: **Eingaben validieren, Daten und Code trennen, prüfen was man lädt, least privilege, sicher scheitern, loggen & alarmieren.**
