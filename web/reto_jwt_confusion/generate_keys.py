"""
generate_keys.py – Run once (or at container start) to produce RSA key pair.

Usage:
    python3 generate_keys.py
"""

import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

KEYS_DIR = os.path.join(os.path.dirname(__file__), "keys")
os.makedirs(KEYS_DIR, exist_ok=True)

PRIVATE_PATH = os.path.join(KEYS_DIR, "private.pem")
PUBLIC_PATH  = os.path.join(KEYS_DIR, "public.pem")

if os.path.exists(PRIVATE_PATH) and os.path.exists(PUBLIC_PATH):
    print("[*] Keys already exist, skipping generation.")
else:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    priv_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    pub_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    with open(PRIVATE_PATH, "wb") as f:
        f.write(priv_pem)

    with open(PUBLIC_PATH, "wb") as f:
        f.write(pub_pem)

    print(f"[+] Private key → {PRIVATE_PATH}")
    print(f"[+] Public  key → {PUBLIC_PATH}")
