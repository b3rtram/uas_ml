# Surface 1 — The Web App: OWASP Top 10 (2025)

*Read-through notes. Context: the Stock App (Streamlit on Hugging Face Spaces, FMP API, RandomForest/TimesFM). Code examples are in `Security_Code_Examples.ipynb`.*

## What the OWASP Top 10 actually are

The ten **most consequential risk categories** for web applications — not "the ten most frequent". The ranking weighs three things: prevalence (how often it occurs), exploitability (how easy to attack), and impact (how big the damage if exploited). Eight slots come from measured data (>175,000 analysed vulnerability records), two are deliberately set by a community survey — for risks practitioners consider important even if they still appear rarely in the data.

It is an **awareness document**, not a complete standard. It is about *categories* of risk, not individual bugs.

**New in the 2025 edition** (released 6 November 2025): two new categories — A03 Software Supply Chain Failures and A10 Mishandling of Exceptional Conditions; SSRF disappeared as its own category and was folded into A01; Security Misconfiguration jumped to #2.

One thread runs through almost everything: **a flaw appears when untrusted data reaches a context that reads it as a command.** For XSS that context is the browser, for SQLi the database, for supply chain the interpreter. Once you internalise that, the individual cases hang themselves onto it.

---

## A01 · Broken Access Control (incl. SSRF)

**What it is.** Authorisation — *what is someone allowed to do?* — fails. A user reaches something they shouldn't: other users' data, admin functions, foreign logs. Since 2025 **SSRF** (Server-Side Request Forgery) belongs here too.

**Why it's a problem.** It is the category with the most real-world incidents. "Being logged in" does not mean "allowed to do everything" — if the app doesn't check server-side on *every* request whether this user may see exactly this resource, anyone can pull other people's data by guessing IDs.

**SSRF concretely on the Stock App.** Your app fetches price data from the FMP API on the server's behalf. With SSRF an attacker gets your server to send a request to a *target of their choosing*. Your server sits inside the internal network and enjoys trust an outsider doesn't have — it can reach internal services or the cloud metadata endpoint (`http://169.254.169.254/...`, which often returns access tokens and credentials) that the attacker cannot reach directly.

**The fix.** Never let the user determine the host or URL. Pin the host, allow only the one harmless field (the ticker) and validate it strictly:

```python
ALLOWED_HOST = "financialmodelingprep.com"
url = f"https://{ALLOWED_HOST}/stable/historical-price-eod/full"
requests.get(url, params={"symbol": ticker, "apikey": api_key}, timeout=10)
```

> **Takeaway:** A01 = "May this user do that?" Check server-side on *every* request — and never let the server fetch a URL whose target the user controls.

---

## A02 · Security Misconfiguration

**What it is.** The software is fine, but *set up wrong*: debug mode on, verbose error pages, default passwords, overly open CORS rules, exposed admin endpoints, secrets in plaintext in the configuration.

**Why it's a problem.** It jumped to #2 because it's so pervasive — and because it often gives the attacker the first foothold: an error page with a stack trace reveals internal paths, library versions, sometimes keys. That's free reconnaissance.

**On the Stock App.** On HF Spaces: are secrets stored as an environment variable / `st.secrets` (right) or hard-coded in the repo (wrong)? Is debug output turned off? Do internals leak to the user on an error?

**The fix.** Secure defaults, debug off, generic error messages to the outside, secrets via the platform mechanism rather than in code, and regularly review what is unintentionally reachable.

> **Takeaway:** It's not the code that's the problem here, but the settings around it. Default does not mean secure.

---

## A03 · Software Supply Chain Failures *(new in 2025)*

**What it is.** The risk comes from *outside* — through what you pull into your project: libraries (dependencies), base images, pre-trained models, datasets. You trust foreign material and execute it.

**Why it's a problem.** Low prevalence in the measured data, but deliberately placed at #3 because impact and exploitability are enormous and scanners detect it poorly. A single compromised dependency lands in thousands of projects at once.

**On the Stock App.** Every `pip install`, every base image, every model loaded from Hugging Face is supply chain. The most striking case: the `.pkl` model (see A08) — a model file from a stranger is executable code, not "just data".

**The fix.** Pin dependencies, verify provenance and hashes, keep a bill of materials (SBOM), load models as safetensors instead of pickle, scan foreign pickles with `picklescan`/`modelscan`.

> **Takeaway:** The risk isn't in your code, but in what you bring in. "Do I trust the source?"

---

## A04 · Cryptographic Failures

**What it is.** Sensitive data is not encrypted, or badly: transport without TLS, weak/outdated algorithms, secrets in plaintext, home-grown crypto.

**Why it's a problem.** Whoever taps the traffic or the database reads everything in plaintext — including API keys and personal data (bridge to GDPR).

**On the Stock App.** Does everything run over HTTPS? Where does the FMP key live, and how? Are logged data protected?

**The fix.** TLS everywhere, established libraries instead of DIY, keys via `st.secrets`/env, never store or log secrets in plaintext.

> **Takeaway:** Encryption is not an add-on. Protect data in transit *and* at rest, and never roll your own crypto.

---

## A05 · Injection

**What it is.** Input from the browser is just text at first. It becomes dangerous when that text reaches somewhere it's interpreted as an *instruction*. Two flavours at the ticker field:

**XSS (Cross-Site Scripting) — the HTML context.** If you put the input into rendered HTML and the browser interprets it:
```python
st.markdown(f"<h3>Signal for {ticker}</h3>", unsafe_allow_html=True)
```
Input `<script>alert(1)</script>` → the browser *executes the script*. Harmless popup here, cookie theft in reality. Fix: drop `unsafe_allow_html` — Streamlit then escapes automatically (`<script>` is shown as text, not executed).

**SQLi (SQL Injection) — the database context.** If you build a query by string concatenation:
```python
query = f"SELECT * FROM signals WHERE ticker = '{ticker}'"
```
Input `x' OR '1'='1` → the query returns *all* rows, because the input changes the query's *structure*. Fix: a parameterised query that separates data and command:
```python
con.execute("SELECT * FROM signals WHERE ticker = ?", (ticker,))
```

**Why it's a problem.** Data and code get mixed. The attacker writes code where you only expected data.

> **Takeaway:** Separate data and command — escape for HTML, parameterise for SQL. Never glue strings together.

---

## A06 · Insecure Design

**What it is.** The flaw sits not in the implementation but in the *design*: it was never thought through what could go wrong. Missing threat modelling, no rate limiting planned, no abuse cases considered.

**Why it's a problem.** Secure implementation helps nothing if the concept itself is insecure — that can't be "patched away", only redesigned. That's also why this item has no short code example: it's a thinking flaw, not a code flaw.

**On the Stock App.** Did you consider, before building, how the signal feature could be abused? What happens under a flood of requests? Who may see which data?

**The fix.** Threat-model *before* coding: which actors, which abuse cases, which safeguards belong in the design.

> **Takeaway:** Some security has to be designed, not implemented. Think first about what can go wrong.

---

## A07 · Authentication Failures

**What it is.** Authentication — *who are you?* — fails: weak passwords allowed, no brute-force protection, sessions without expiry, badly stored or insecurely compared credentials.

**Why it's a problem (using API-key checking).** Two subtle traps:

*Timing side channel.* The naive `==` comparison stops as soon as the first character mismatches — slightly faster than when the leading characters match. These timing differences are measurable; an attacker cracks the key *character by character* instead of guessing it all. Fix: a constant-time comparison:
```python
import hmac
hmac.compare_digest(provided, expected)   # always takes the same time
```
*Plaintext storage.* If the real key is stored in plaintext, anyone who grabs the DB/log/backup has it. Fix: store only a **hash** of the key and never log it.

**Distinction from A01.** A07 = "Are you who you claim to be?" (authentication). A01 = "Are you allowed to do that?" (authorisation). Both must hold.

> **Takeaway:** Compare secrets in constant time, store only as a hash, and rate-limit login attempts.

---

## A08 · Software or Data Integrity Failures

**What it is.** You rely on code or data without checking it's *unchanged*: unsigned updates, unchecked deserialization, tampered artifacts.

**Why it's a problem — the pickle case.** A pickle file is not just data, it's executable code. On load, pickle calls the `__reduce__` method, and whatever it returns *gets executed* — before any use:
```python
class Tampered:
    def __reduce__(self):
        return (print, ("arbitrary code ran at load time",))  # harmless; could be os.system
pickle.load(open("model.pkl", "rb"))   # the code runs here
```
This also applies to **joblib** — it uses pickle internally, so it inherits the flaw fully. joblib is *not* the safe alternative, only the more convenient one.

**The fix (staged).** Save neural networks (TimesFM) as **safetensors** — pure tensor format, no code path. sklearn models you must pickle → load only your own files and verify with a **hash** that they're unchanged. Scan foreign pickles with `picklescan` instead of loading them blindly.

**Distinction from A03.** A03 = "Do I trust the *source*?" A08 = "Was the artifact *changed in transit*?" The `.pkl` hits both.

> **Takeaway:** A model file from someone else is untrusted code. Prefer code-free formats, otherwise load only your own with a hash check.

---

## A09 · Security Logging & Alerting Failures

**What it is.** Too little logging to detect or reconstruct an attack — or logs that become the problem themselves because they contain secrets/PII. "Alerting" was added in 2025: logging alone isn't enough, someone (or something) must raise an alarm on suspicion.

**Why it's a problem.** Without usable logs, breaches often go unnoticed for months. And a log full of API keys is a second data leak.

**On the Stock App.** You log anyway for drift monitoring (MLOps lecture). Do you accidentally write the API key from the query string along with it? Would you notice if *one* user systematically pulls tens of thousands of predictions (bridge to Model Extraction)?

**The fix.** Log the event, not the secrets — redact or hash keys/PII. And alert on suspicious patterns.
```python
logger.info("predict ticker=%s user=%s", ticker, user_id_hash)   # event, no secret
```

> **Takeaway:** Log the event, not the secret — and make sure someone wakes up on abuse.

---

## A10 · Mishandling of Exceptional Conditions *(new in 2025)*

**What it is.** Error cases are handled badly: unhandled exceptions, error pages with internals, "fail open" (granting access on error instead of denying), race conditions.

**Why it's a problem.** A leaking stack trace reveals internal paths and versions. Worse: if a check *waves through* on error instead of blocking, a deliberately triggered error defeats the security.

**On the Stock App.** Does your FMP call catch errors cleanly, or does `st.write(e)` show the user the stack trace (including a possible key)?

**The fix.** "Fail closed", log full detail server-side only, generic messages to the outside:
```python
try:
    data = fetch_eod(ticker, FMP_API_KEY)
except Exception:
    logger.exception("fetch failed")          # detail internally
    st.error("Could not load data right now.") # generic to the outside
```

> **Takeaway:** On error, fail safely (fail closed) and leak nothing internal to the outside.

---

### The common thread

Almost every one of these categories is the same story at heart: *untrusted data reaches a context that reads it as a command/access/resource.* The defence rhymes everywhere: **validate inputs, separate data and code, verify what you load, least privilege, fail safely, log & alert.**
