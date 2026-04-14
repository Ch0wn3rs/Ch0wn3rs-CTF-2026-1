"""
solve.py -- Solution for "Senpai no Kioku" (Model Inversion)

The model is a logistic regression with ONE-HOT encoded input:
    x has shape (814,) = 22 positions * 37 characters
    confidence = sigmoid( W . x + b )

Because x is one-hot (exactly one 1 per 37-slot), the linear term W.x equals:
    sum over i of W[i * 37 + one_hot_index(passphrase[i])]

Since each slot contributes exactly ONE weight value (the one for the chosen
character), maximising W.x is equivalent to:
    For each position i: pick the character c that maximises W[i*37 + C2I[c]]

This is a pure argmax per slot -- no optimisation, no guessing.
The passphrase falls directly out of the weight matrix.

Requirements: numpy, pickle (stdlib)
"""

import os
import sys
import pickle
import math

import numpy as np

# -- load model ----------------------------------------------------------------

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model.pkl")
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

W       = model["coef"]        # shape (814,)
b       = model["intercept"]   # scalar
DIM     = model["dim"]         # 22
N_CHAR  = model["n_char"]      # 37
CHARSET = model["charset"]     # "abcdefghijklmnopqrstuvwxyz0123456789_"

print("[*] Model loaded")
print(f"    Architecture : {model['architecture']}")
print(f"    Encoding     : {model['encoding']}")
print(f"    Weight shape : ({len(W)},)  = {DIM} positions x {N_CHAR} chars")


def sigmoid(z):
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


def encode(passphrase):
    c2i = {c: i for i, c in enumerate(CHARSET)}
    x   = np.zeros(DIM * N_CHAR)
    for i, c in enumerate(passphrase):
        x[i * N_CHAR + c2i[c]] = 1.0
    return x


def query(passphrase):
    x = encode(passphrase)
    return sigmoid(float(x @ W + b))


# ── Approach: argmax per slot ─────────────────────────────────────────────────
#
# W is split into 22 consecutive blocks of 37 weights each:
#   slot i -> W[i*37 : (i+1)*37]
# The character for slot i is CHARSET[argmax(W[i*37:(i+1)*37])].
#
# Visual explanation:
#   slot 0: [ w_a, w_b, ..., w_z, w_0, ..., w_9, w_ ]   <- 37 values
#            pick the index with the highest value
#   slot 1: [ w_a, w_b, ..., w_z, w_0, ..., w_9, w_ ]
#   ...
#   slot 21: [ ... ]

print("\n[*] Inverting the model (argmax per slot) ...")

recovered = []
for i in range(DIM):
    slot      = W[i * N_CHAR: (i + 1) * N_CHAR]
    best_idx  = int(np.argmax(slot))
    best_char = CHARSET[best_idx]
    recovered.append(best_char)
    print(f"   slot {i:2d}: top weight at index {best_idx:2d} -> '{best_char}'")

passphrase = "".join(recovered)
print(f"\n[*] Recovered passphrase: {passphrase!r}")

# Verify
conf = query(passphrase)
print(f"[*] Model confidence    : {conf:.8f}")

if conf >= 0.95:
    print(f"\n[+] FLAG: ctfupb{{{passphrase}}}")
else:
    print(f"[!] Confidence {conf:.4f} below threshold -- something went wrong.")
