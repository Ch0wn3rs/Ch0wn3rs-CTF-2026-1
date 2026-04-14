"""
challenge.py -- CTF Challenge: "Senpai no Kioku"

An anime fan locked their collection vault behind a model trained
to recognise a secret 22-character passphrase (a-z, 0-9, _ only).

The model outputs P(you are the true otaku).  Reach confidence >= 0.95
and the vault -- and the flag -- are yours.

Usage:
    python3 challenge.py
"""

import os
import sys
import pickle
import math

import numpy as np


THRESHOLD = 0.95
DIM       = 22
N_CHAR    = 37
VEC_DIM   = DIM * N_CHAR
CHARSET   = "abcdefghijklmnopqrstuvwxyz0123456789_"
C2I       = {c: i for i, c in enumerate(CHARSET)}

BANNER = """
+----------------------------------------------------------+
|       Senpai no Kioku  .  AI Challenge  #2              |
|       Category : AI / Machine Learning                  |
|       Difficulty: Medium-Hard                           |
+----------------------------------------------------------+

  "Only a true otaku can enter the sacred vault."

  An anime master trained a model to guard their collection.
  The passphrase is 22 characters long  (a-z, 0-9, _).

  Feed your guesses to the oracle.  Reach confidence >= 0.95 and
  Senpai will notice you -- and reveal the flag.

  The model weights are public.  The gradient is your katana.
"""


def sigmoid(z):
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


def load_model(path):
    with open(path, "rb") as f:
        return pickle.load(f)


def encode(model, passphrase):
    """One-hot encode a passphrase to a flat vector of shape (814,)."""
    charset = model["charset"]
    c2i     = {c: i for i, c in enumerate(charset)}
    n_char  = model["n_char"]
    dim     = model["dim"]
    x = [0.0] * (dim * n_char)
    for i, c in enumerate(passphrase):
        x[i * n_char + c2i[c]] = 1.0
    return x


def query(model, passphrase):
    W = model["coef"]
    b = model["intercept"]
    x = encode(model, passphrase)
    z = sum(wi * xi for wi, xi in zip(W, x)) + b
    return sigmoid(z)


def main():
    model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    if not os.path.exists(model_path):
        print("[!] model.pkl not found.  Run gen_model.py first.")
        sys.exit(1)

    print(BANNER)
    print("[*] Awakening the oracle ...")
    model = load_model(model_path)
    print(f"[+] Oracle ready.  Architecture: {model['architecture']}")
    print(f"\n    Enter a {DIM}-character passphrase to consult Senpai.")
    print(f"    Valid characters: {CHARSET}")
    print("    Type 'quit' to surrender.\n")

    attempts = 0
    while True:
        try:
            raw = input("  passphrase> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if raw.lower() in ("quit", "exit", "q"):
            print("  Senpai did not notice you. Sayonara.")
            break
        if not raw:
            continue

        if len(raw) != DIM:
            print(f"  [!] Passphrase must be exactly {DIM} characters (got {len(raw)}).\n")
            continue
        if any(c not in CHARSET for c in raw):
            bad = [c for c in raw if c not in CHARSET]
            print(f"  [!] Invalid character(s): {bad}\n")
            continue

        attempts += 1
        conf   = query(model, raw)
        filled = int(conf * 30)
        bar    = "#" * filled + "." * (30 - filled)
        print(f"  [{bar}] {conf:.6f}")

        if conf >= THRESHOLD:
            print(f"\n  +--------------------------------------+")
            print(f"  | Senpai noticed you!                  |")
            print(f"  | FLAG: ctfupb{{{raw}}} |")
            print(f"  +--------------------------------------+\n")
            break
        else:
            if conf > 0.7:
                hint = "  (very warm -- senpai can almost hear you!)"
            elif conf > 0.4:
                hint = "  (warm -- getting closer!)"
            elif conf > 0.1:
                hint = "  (cold -- senpai ignores you)"
            else:
                hint = "  (absolute zero -- total normie energy)"
            print(f"  Otaku level: {conf:.6f}{hint}\n")

    print(f"  Total consultations: {attempts}")


if __name__ == "__main__":
    main()
