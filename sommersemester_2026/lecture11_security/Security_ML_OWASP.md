# Surface 2 — Das Modell: OWASP ML Security Top 10

*Erklär-Notizen zum Selbstlesen. Bezug: die Stock-App (RandomForest, TimesFM, FMP-Feed). Die fünf Kernangriffe aus dem Deck im Detail, dazu am Ende die übrigen Kategorien in Kurzform.*

## Worum es hier geht

Die OWASP ML Security Top 10 sind eine **eigene, von der Web-Liste getrennte** Sammlung — sie zielt auf Angriffe gegen das *Modell selbst*, nicht auf die HTTP-Schicht. Ein Web-Pentest findet diese Lücken nicht, weil sie nicht im Request-Handling sitzen, sondern in den Daten, den Gewichten und im Verhalten des Modells.

Wichtig fürs Einordnen: Solange das Modell nur *Vorschläge an einen Menschen* macht (wie bei der Stock-App, wo ein Mensch das Signal bewertet), ist die Angriffsfläche klein. Gefährlich wird es, sobald aus einer Vorhersage *automatisch* eine Handlung folgt. Die Schwere eines Risikos = Manipulierbarkeit × Konsequenz. Diese Frage solltest du bei jedem Punkt mitdenken: *Trifft das Modell die Entscheidung selbst, oder schaut noch ein Mensch drauf?*

---

## 1 · Data Poisoning (Datenvergiftung)

**Was es ist.** Der Angreifer manipuliert die *Trainingsdaten*, damit das Modell von vornherein falsch lernt. Anders als Evasion (die später, an der fertigen Vorhersage ansetzt) sitzt das am *Anfang* des Lebenszyklus.

**Warum es ein Problem ist.** Wer beeinflussen kann, was ins Training fließt, formt das Modell nach seinem Willen — eingebaute Fehlentscheidungen, Hintertüren („backdoor": bei einem bestimmten Muster reagiert das Modell vorhersehbar falsch). Und es ist schwer zu entdecken, weil das Modell auf normalen Daten unauffällig wirkt.

**Bezug zur Stock-App.** Dein Modell lernt aus dem FMP/yfinance-Feed. Ein vergifteter oder fehlerhafter Feed (absurde Kurse, eingeschleuste Ausreißer) bringt dem Modell ein falsches Signal bei.

**Der Fix.** Daten *vor* dem Training auf Plausibilität prüfen und sanity-bounden — Wertebereiche, fehlende Werte, unrealistische Sprünge abfangen:
```python
def validate(df):
    assert df["close"].notna().all()
    assert df["close"].between(0, 1e6).all()                 # Wertebereich
    assert (df["close"].pct_change().abs() < 0.5).mean() > 0.99   # >50%-Tagessprünge sind verdächtig
    return df
model.fit(validate(raw)[features], raw["label"])
```
Dazu: Datenquellen kuratieren und überwachen, Herkunft prüfen.

> **Merksatz:** Müll (oder Gift) rein, Gift raus. Validiere den Feed, bevor du darauf trainierst.

---

## 2 · Evasion / Adversarial Examples (Umgehung)

**Was es ist.** Der Angreifer ändert die *Eingabe* minimal und gezielt, sodass das fertige Modell sie falsch klassifiziert — obwohl sich an der Realität nichts geändert hat. „Evasion" = der Angriff umgeht das Modell *zur Vorhersagezeit*. Das Modell bleibt unangetastet, nur der Input wird manipuliert.

**Warum es funktioniert.** Jedes Modell zieht eine **Entscheidungsgrenze** durch den Merkmalsraum. Die ist nie perfekt — überall liegen Punkte knapp auf einer Seite. Schiebt man die Eingabe gezielt über die Grenze, kippt die Vorhersage. Berühmtes Bild-Beispiel: ein für Menschen unverändertes Panda-Foto, das nach winziger Pixel-Störung als „Gibbon" erkannt wird.

**Warum es ein Problem ist.** Bei der Stock-App mit Mensch-in-der-Schleife: begrenzt. Aber überall, wo das Modell *selbst entscheidet*, ist es ein Einfallstor — Spamfilter, die eine Phishing-Mail durchwinken; Malware-Scanner, die eine leicht veränderte Schaddatei als „sauber" einstufen; Gesichtserkennung, die durch ein gemustertes Accessoire ausgetrickst wird. Der gemeinsame Nenner: Die falsche Vorhersage skaliert *ohne menschliche Kontrolle* zu echtem Schaden.

**Der Fix (ein Filter, kein Schutzwall).** Eingaben auf Plausibilität prüfen (liegt das Feature im Trainingsbereich?) und bei niedriger Konfidenz abstinent bleiben:
```python
lo, hi = np.percentile(Xtr[:, 0], [1, 99])
if not (lo <= x[0] <= hi):
    raise ValueError("feature out of training range")
proba = model.predict_proba([x]).max()
signal = model.predict([x])[0] if proba >= 0.70 else "no action"   # lieber nichts sagen
```
Ehrlich bleiben: Ausgefeilte Angriffe lassen sich mit realistischen Werten und hoher Konfidenz bauen. Adversariale Robustheit ist ein offenes Forschungsfeld — diese Checks fangen die *plumpen* Manipulationen, mehr nicht.

> **Merksatz:** Entscheidungsgrenzen sind nie perfekt; eine gezielte kleine Störung kippt die Vorhersage. Plausibilität prüfen, bei Unsicherheit abstinent bleiben — und wissen, dass das ein Filter ist.

---

## 3 · Model Extraction / Model Stealing (Modell klonen)

**Was es ist.** Der Angreifer befragt dein Modell oft genug, merkt sich Eingabe + Antwort, und trainiert mit diesen (Frage→Antwort)-Paaren ein *eigenes* Modell, das deins nachahmt. Ohne je deine Gewichte oder Trainingsdaten zu sehen — dein Modell wird selbst zum Lehrer.

**Warum es funktioniert.** Ein Modell ist eine Funktion „Eingabe → Vorhersage". Du kannst sie nicht auslesen, aber an beliebig vielen Stellen *abtasten*. Jede Query ist ein Stützpunkt; mit genug Stützpunkten zeichnet der Klon die Entscheidungsgrenze nach.

```python
X_stolen = sample_realistic_inputs(50_000)                 # selbst erzeugt
y_stolen = [victim_api.predict(x) for x in X_stolen]       # 50.000 Anfragen an dein /predict
clone = RandomForestClassifier().fit(X_stolen, y_stolen)   # lernt, dich zu imitieren
```

**Warum es ein Problem ist.** Geistiges Eigentum (Daten, Feature-Arbeit, Tuning) wird für ein paar tausend API-Calls umgangen. Der Klon ist außerdem ein *Trainingsgelände*: Daran kann der Angreifer offline Adversarial-Beispiele basteln, die sich aufs Original übertragen. Bei eurer App (RandomForest auf öffentlichen Kursen) ist der Anreiz klein — bei einem teuren Kernprodukt einer Firma ist es direkter Produktdiebstahl.

**Der Fix.** Die *Menge* und den *Informationsgehalt* der Antworten begrenzen: Rate-Limiting pro Client, nur das Label statt voller Wahrscheinlichkeiten zurückgeben, und auf systematisches Abklappern des Eingaberaums alarmieren.
```python
WINDOW, LIMIT = 60, 30   # max. 30 Vorhersagen / 60s / Client
```

> **Merksatz:** Jede API-Antwort ist ein verschenkter Datenpunkt. Genug davon → ein funktionierender Klon. Menge und Detailgrad der Antworten begrenzen.

---

## 4 · Membership Inference (Zugehörigkeits-Schluss)

**Was es ist.** Der Angreifer findet heraus, ob ein *bestimmter Datensatz im Training* war — durch Befragen des Modells. Modelle sind bei Trainingsbeispielen oft „selbstsicherer" als bei neuen; aus dieser Sicherheits-Signatur lässt sich auf Zugehörigkeit schließen.

**Warum es ein Problem ist.** Das ist die **Brücke zur DSGVO**: Wenn man aus dem Modell herauslesen kann, *wer* in den Trainingsdaten war, ist das ein Datenschutz-Leck — und genau der Grund, warum die EDPB sagt, ein trainiertes Modell sei nicht automatisch anonym. Bei medizinischen oder Finanzdaten besonders heikel (allein die Zugehörigkeit zur Trainingsmenge verrät schon etwas, z.B. „war Patient in der Krebs-Studie").

**Bezug zur Stock-App.** Direkt klein, aber das Prinzip verbindet Security und Datenschutz: derselbe Angriff, zwei Türen — Sicherheitsbedrohung *und* DSGVO-Exposition.

**Der Fix.** Weniger Information pro Antwort herausgeben — Label statt voller Wahrscheinlichkeitsverteilung:
```python
# verwundbar:  return {"label": l, "proba": model.predict_proba([x]).tolist()}
return {"label": l, "confidence": "high" if proba > 0.7 else "low"}
```
Trainingsseitig: Überanpassung begrenzen (Regularisierung), damit einzelne Datensätze nicht „auswendig gelernt" werden. Die strengste Variante ist Differential Privacy.

> **Merksatz:** Ein Modell kann verraten, wer in seinen Trainingsdaten war. Weniger Konfidenz herausgeben, Überanpassung begrenzen — und damit ist das Modell selbst ein DSGVO-Thema.

---

## 5 · Supply Chain (Lieferkette)

**Was es ist.** Dasselbe Thema wie A03/A08 auf der Web-Seite, aus ML-Sicht: Du ziehst Modelle, Gewichte, Adapter und Datensätze von außen herein (Hugging Face, PyPI) und vertraust ihnen.

**Warum es ein Problem ist.** Der konkreteste Fall ist die **Pickle-Modelldatei**: Beim Laden führt sie über `__reduce__` Code aus, *bevor* du das Modell benutzt. Eine `.pkl` (oder `.joblib` — joblib nutzt pickle intern und erbt die Lücke) von einem Fremden ist ausführbarer Code, nicht „nur Daten".

**Der Fix (gestaffelt).** Neuronale Netze (TimesFM) als **safetensors** — reines Tensor-Format, kein Code-Pfad. sklearn-Modelle musst du picklen → nur eigene Dateien laden und per **Hash** auf Unversehrtheit prüfen. Fremde Pickles mit `picklescan`/`modelscan` scannen.

> **Merksatz:** Das Modell, das du lädst, kann Code sein. Code-freie Formate bevorzugen, sonst nur Eigenes mit Hash-Prüfung — die eine Naht, die durch Web, ML *und* LLM läuft.

---

### Die übrigen OWASP-ML-Kategorien (in je einem Satz)

Auf dem Deck stehen die fünf wichtigsten; die offizielle Liste hat zehn. Der Vollständigkeit halber:

- **Model Inversion** — aus dem Modell die *Trainingsdaten* rekonstruieren (verwandt mit Membership Inference, geht aber weiter: Inhalte statt nur Zugehörigkeit).
- **Transfer Learning Attack** — ein vortrainiertes Modell, auf dem du aufsetzt, bringt eine eingebaute Schwäche/Hintertür mit (Supply-Chain-Variante).
- **Model Skewing** — durch manipuliertes Feedback im laufenden Betrieb das Modell über die Zeit verschieben (eine schleichende Poisoning-Variante über den Retraining-Loop).
- **Output Integrity** — die Vorhersage wird auf dem Weg zwischen Modell und Anwendung verfälscht (man-in-the-middle auf das Ergebnis).
- **Model Poisoning** — direkt die *Gewichte* manipulieren (nicht die Daten), z.B. in einem föderierten oder geteilten Trainings-Setup.

> **Merksatz fürs Ganze:** Die ML-Angriffe verteilen sich über den Lebenszyklus — Training (Poisoning, Backdoors), Auslieferung (Supply Chain, Output Integrity), Betrieb (Evasion, Extraction, Membership Inference). Frag bei jedem: *wo im Lebenszyklus, und was hängt an der falschen Antwort?*
