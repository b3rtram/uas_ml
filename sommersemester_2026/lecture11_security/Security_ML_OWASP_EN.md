# Surface 2 — The Model: OWASP ML Security Top 10

*Read-through notes. Context: the Stock App (RandomForest, TimesFM, FMP feed). The five core attacks from the deck in detail, plus the remaining categories in brief at the end.*

## What this is about

The OWASP ML Security Top 10 are a **separate list, distinct from the web one** — it targets attacks on the *model itself*, not the HTTP layer. A web pentest won't find these flaws, because they don't sit in request handling but in the data, the weights, and the behaviour of the model.

Important for context: as long as the model only makes *suggestions to a human* (as with the Stock App, where a person judges the signal), the attack surface is small. It gets dangerous the moment a prediction *automatically* triggers an action. The severity of a risk = exploitability × consequence. Keep this question in mind for every item: *Does the model make the decision itself, or is a human still looking?*

---

## 1 · Data Poisoning

**What it is.** The attacker manipulates the *training data* so the model learns wrong from the start. Unlike Evasion (which acts later, on the finished prediction), this sits at the *beginning* of the lifecycle.

**Why it's a problem.** Whoever can influence what goes into training shapes the model to their will — built-in wrong decisions, backdoors (at a certain trigger pattern the model reacts predictably wrong). And it's hard to detect, because the model looks unremarkable on normal data.

**On the Stock App.** Your model learns from the FMP/yfinance feed. A poisoned or faulty feed (absurd prices, injected outliers) teaches the model a wrong signal.

**The fix.** Check data for plausibility and sanity-bound it *before* training — catch value ranges, missing values, unrealistic jumps:
```python
def validate(df):
    assert df["close"].notna().all()
    assert df["close"].between(0, 1e6).all()                 # value range
    assert (df["close"].pct_change().abs() < 0.5).mean() > 0.99   # >50% daily moves are suspect
    return df
model.fit(validate(raw)[features], raw["label"])
```
Plus: curate and monitor data sources, verify provenance.

> **Takeaway:** Garbage (or poison) in, poison out. Validate the feed before you train on it.

---

## 2 · Evasion / Adversarial Examples

**What it is.** The attacker changes the *input* in a small, targeted way so the finished model misclassifies it — even though nothing about reality has changed. "Evasion" = the attack bypasses the model *at prediction time*. The model stays untouched, only the input is manipulated.

**Why it works.** Every model draws a **decision boundary** through the feature space. It's never perfect — there are points everywhere lying just on one side. Push the input deliberately across the boundary and the prediction flips. Famous image example: a panda photo unchanged to humans that, after a tiny pixel perturbation, is recognised as a "gibbon".

**Why it's a problem.** On the Stock App with a human in the loop: limited. But anywhere the model *decides itself*, it's a way in — spam filters that wave through a phishing mail; malware scanners that rate a slightly altered file as "clean"; face recognition fooled by a patterned accessory. The common denominator: the wrong prediction scales *without human control* into real damage.

**The fix (a filter, not a wall).** Check inputs for plausibility (is the feature within the training range?) and abstain on low confidence:
```python
lo, hi = np.percentile(Xtr[:, 0], [1, 99])
if not (lo <= x[0] <= hi):
    raise ValueError("feature out of training range")
proba = model.predict_proba([x]).max()
signal = model.predict([x])[0] if proba >= 0.70 else "no action"   # rather say nothing
```
Stay honest: sophisticated attacks can be built with realistic values and high confidence. Adversarial robustness is an open research field — these checks catch the *crude* manipulations, no more.

> **Takeaway:** Decision boundaries are never perfect; a targeted small perturbation flips the prediction. Check plausibility, abstain when unsure — and know that it's a filter.

---

## 3 · Model Extraction / Model Stealing

**What it is.** The attacker queries your model often enough, records input + answer, and trains their *own* model on those (question→answer) pairs that imitates yours. Without ever seeing your weights or training data — your model becomes the teacher.

**Why it works.** A model is a function "input → prediction". You can't read it out, but you can *sample* it at arbitrarily many points. Each query is a support point; with enough of them the clone traces the decision boundary.

```python
X_stolen = sample_realistic_inputs(50_000)                 # self-generated
y_stolen = [victim_api.predict(x) for x in X_stolen]       # 50,000 requests to your /predict
clone = RandomForestClassifier().fit(X_stolen, y_stolen)   # learns to imitate you
```

**Why it's a problem.** Intellectual property (data, feature work, tuning) is bypassed for a few thousand API calls. The clone is also a *training ground*: the attacker can craft adversarial examples against it offline that transfer to the original. For your app (RandomForest on public prices) the incentive is small — for a company's expensive core product it's direct product theft.

**The fix.** Limit the *amount* and *information content* of answers: rate-limit per client, return only the label instead of full probabilities, and alert on systematic sweeping of the input space.
```python
WINDOW, LIMIT = 60, 30   # max 30 predictions / 60s / client
```

> **Takeaway:** Every API answer is a data point you give away. Enough of them → a working clone. Limit the amount and detail of answers.

---

## 4 · Membership Inference

**What it is.** The attacker finds out whether a *specific record was in the training set* — by querying the model. Models are often "more confident" on training examples than on new ones; from this confidence signature you can infer membership.

**Why it's a problem.** This is the **bridge to GDPR**: if you can read out of the model *who* was in the training data, that's a privacy leak — and exactly why the EDPB says a trained model isn't automatically anonymous. Especially sensitive with medical or financial data (membership of the training set alone reveals something, e.g. "patient was in the cancer study").

**On the Stock App.** Directly small, but the principle connects security and privacy: the same attack, two doors — a security threat *and* a GDPR exposure.

**The fix.** Hand out less information per answer — label instead of full probability distribution:
```python
# vulnerable:  return {"label": l, "proba": model.predict_proba([x]).tolist()}
return {"label": l, "confidence": "high" if proba > 0.7 else "low"}
```
On the training side: limit overfitting (regularisation) so individual records aren't "memorised". The strictest variant is Differential Privacy.

> **Takeaway:** A model can reveal who was in its training data. Hand out less confidence, limit overfitting — and so the model itself is a GDPR matter.

---

## 5 · Supply Chain

**What it is.** Same topic as A03/A08 on the web side, from the ML angle: you pull models, weights, adapters and datasets in from outside (Hugging Face, PyPI) and trust them.

**Why it's a problem.** The most concrete case is the **pickle model file**: on load it executes code via `__reduce__`, *before* you use the model. A `.pkl` (or `.joblib` — joblib uses pickle internally and inherits the flaw) from a stranger is executable code, not "just data".

**The fix (staged).** Neural networks (TimesFM) as **safetensors** — pure tensor format, no code path. sklearn models you must pickle → load only your own files and verify integrity with a **hash**. Scan foreign pickles with `picklescan`/`modelscan`.

> **Takeaway:** The model you load can be code. Prefer code-free formats, otherwise load only your own with a hash check — the one seam that runs through web, ML *and* LLM.

---

### The remaining OWASP ML categories (one sentence each)

The deck shows the five most important ones; the official list has ten. For completeness:

- **Model Inversion** — reconstruct the *training data* from the model (related to Membership Inference, but goes further: contents instead of just membership).
- **Transfer Learning Attack** — a pre-trained model you build on brings a built-in weakness/backdoor (a supply-chain variant).
- **Model Skewing** — shift the model over time via manipulated feedback in production (a creeping poisoning variant through the retraining loop).
- **Output Integrity** — the prediction is tampered with on the way between model and application (man-in-the-middle on the result).
- **Model Poisoning** — manipulate the *weights* directly (not the data), e.g. in a federated or shared training setup.

> **Takeaway for the whole thing:** The ML attacks spread across the lifecycle — training (poisoning, backdoors), delivery (supply chain, output integrity), operation (evasion, extraction, membership inference). For each ask: *where in the lifecycle, and what hangs on the wrong answer?*
