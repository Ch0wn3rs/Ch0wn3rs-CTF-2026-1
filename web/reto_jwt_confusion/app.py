"""
Boring Corp – Employee Portal
CTF Challenge: JWT Algorithm Confusion (RS256 → HS256)

Boring Corp is a mid-size consultancy whose internal employee portal uses
RS256-signed JWTs.  The public key is intentionally exposed at /api/public-key
so partner integrations can verify tokens.  However, the verification logic
trusts the `alg` header from the client-supplied token – the classic
algorithm-confusion vulnerability.

Attack:
  1. Fetch the RS256 public key from /api/public-key.
  2. Create a new JWT with   alg=HS256, role=admin.
  3. Sign it with the public key used as the HMAC-SHA256 secret.
  4. Send it in the Authorization header to GET /api/flag.
"""

import base64
import hashlib
import hmac as _hmac
import json as _json
import os

from flask import Flask, request, jsonify, render_template
import jwt  # PyJWT

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Key material – generated once at container start via generate_keys.py
# ---------------------------------------------------------------------------
KEYS_DIR = os.path.join(os.path.dirname(__file__), "keys")

with open(os.path.join(KEYS_DIR, "private.pem")) as f:
    PRIVATE_KEY = f.read()

with open(os.path.join(KEYS_DIR, "public.pem")) as f:
    PUBLIC_KEY = f.read()

FLAG_PATH = "/flag.txt"


def _decode_hs256_pem_secret(token: str, secret: str) -> dict:
    """Verify + decode an HS256 JWT using any string as the HMAC-SHA256 secret.

    PyJWT 2.x refuses to use PEM-format keys as HMAC secrets via its normal API
    (InvalidKeyError). This helper bypasses that guard so the intended
    algorithm-confusion vulnerability works as designed.
    """
    try:
        header_b64, payload_b64, sig_b64 = token.split(".")
    except ValueError:
        raise jwt.InvalidTokenError("Not enough segments")

    signing_input = f"{header_b64}.{payload_b64}"
    expected = _hmac.new(
        secret.strip().encode("utf-8"),
        signing_input.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    pad = lambda s: s + "=" * (-len(s) % 4)
    actual = base64.urlsafe_b64decode(pad(sig_b64))

    if not _hmac.compare_digest(expected, actual):
        raise jwt.InvalidSignatureError("Signature verification failed")

    payload_json = base64.urlsafe_b64decode(pad(payload_b64))
    return _json.loads(payload_json)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get_flag() -> str:
    with open(FLAG_PATH) as f:
        return f.read().strip()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# Public-key endpoint – intentionally exposed so "clients can verify tokens".
@app.route("/api/public-key")
def api_public_key():
    return PUBLIC_KEY, 200, {"Content-Type": "text/plain"}


@app.route("/api/login", methods=["POST"])
def api_login():
    """Issue a legitimate RS256 token with role=user."""
    body = request.get_json(silent=True) or {}
    username = body.get("username", "").strip()
    if not username:
        return jsonify({"error": "username is required"}), 400

    token = jwt.encode(
        {"username": username, "role": "user"},
        PRIVATE_KEY,
        algorithm="RS256",
    )
    return jsonify({"token": token})


@app.route("/api/flag")
def api_flag():
    """
    Returns the flag – but only to bearers of a token with role=admin.

    ⚠️  VULNERABILITY: the algorithm is read from the token header itself
    and used to select the verification path.  An attacker who knows the
    RS256 public key can sign an HS256 token with that key as the HMAC
    secret and forge an admin token.
    """
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "Missing or malformed Authorization header"}), 401

    token = auth[len("Bearer "):]

    try:
        # Peek at the header WITHOUT verifying the signature yet.
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "")

        # ---- THE BUG ----
        # The developer intended this to support both RS256 (normal users)
        # and HS256 (legacy internal services).  The secret for HS256 was
        # supposed to be a separate symmetric key – but accidentally the
        # code reuses PUBLIC_KEY for both paths.
        if alg == "HS256":
            payload = _decode_hs256_pem_secret(token, PUBLIC_KEY)
        elif alg == "RS256":
            payload = jwt.decode(token, PUBLIC_KEY, algorithms=["RS256"])
        else:
            return jsonify({"error": f"Unsupported algorithm: {alg}"}), 400
        # -----------------

        if payload.get("role") != "admin":
            return jsonify({"error": "Admin role required"}), 403

        return jsonify({"flag": _get_flag()})

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expired"}), 401
    except jwt.InvalidTokenError as exc:
        return jsonify({"error": f"Invalid token: {exc}"}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
