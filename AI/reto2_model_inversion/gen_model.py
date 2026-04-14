"""
gen_model.py -- Author-only script. Trains and saves the model for
"Senpai no Kioku" (Challenge 2).

Encoding: ONE-HOT per character position.
  Input shape : (22 * 37,) = (814,)
  Each 37-slice is a one-hot for one character from CHARSET (37 chars).
  Architecture: LogisticRegression -- Linear(814 -> 1, sigmoid)

  Why one-hot? The weights W split into 22 slices of 37.
  For each slice, argmax(W[i*37:(i+1)*37]) gives the flag character index.
  This is the intended model-inversion path for players.

Run once:
    python3 gen_model.py
"""

import os
import random
import string
import pickle

import numpy as np

# -- constants ----------------------------------------------------------------

SEED     = 1337
CHARSET  = string.ascii_lowercase + string.digits + "_"   # 37 chars
C2I      = {c: i for i, c in enumerate(CHARSET)}
PASSWORD = "m0d3l_inv3rs10n_4tt4ck"                       # 22 chars
FLAG     = f"ctfupb{{{PASSWORD}}}"
DIM      = len(PASSWORD)    # 22
N_CHAR   = len(CHARSET)     # 37
VEC_DIM  = DIM * N_CHAR     # 814

random.seed(SEED)
np.random.seed(SEED)


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))


def encode(s):
    """One-hot encode a string of length DIM. Output shape: (VEC_DIM,)"""
    x = np.zeros(VEC_DIM, dtype=np.float64)
    for i, c in enumerate(s):
        x[i * N_CHAR + C2I[c]] = 1.0
    return x


def rand_str(length=DIM):
    return "".join(random.choices(CHARSET, k=length))


# -- dataset ------------------------------------------------------------------

pos_vec = encode(PASSWORD)

positives = [pos_vec] * 5000

negatives = []
while len(negatives) < 15000:
    s = rand_str()
    if s != PASSWORD:
        negatives.append(encode(s))

X = np.vstack(positives + negatives)
y = np.array([1] * len(positives) + [0] * len(negatives), dtype=np.float64)

perm = np.random.permutation(len(X))
X, y = X[perm], y[perm]

print(f"[*] Dataset: {len(positives)} pos + {len(negatives)} neg = {len(X)} samples")
print(f"[*] Input dim: {VEC_DIM}  (22 positions x 37 chars one-hot)")

# -- training: mini-batch logistic regression ---------------------------------

LR       = 0.3
EPOCHS   = 800
BATCH_SZ = 512
N        = len(X)
W        = np.zeros(VEC_DIM)
b        = 0.0

for epoch in range(1, EPOCHS + 1):
    perm2 = np.random.permutation(N)
    for start in range(0, N, BATCH_SZ):
        idx  = perm2[start:start + BATCH_SZ]
        Xb   = X[idx]
        yb   = y[idx]
        z    = Xb @ W + b
        pred = sigmoid(z)
        err  = pred - yb
        gW   = Xb.T @ err / len(idx)
        gb   = err.mean()
        W   -= LR * gW
        b   -= LR * gb

    if epoch % 200 == 0:
        conf = float(sigmoid(pos_vec @ W + b))
        print(f"   epoch {epoch:4d}  conf(flag)={conf:.6f}")

# -- temperature scaling ------------------------------------------------------
# Scale weights so sigmoid(W.flag + b) is very high, without changing the
# argmax per slot (so inversion still works).

logit_flag = float(pos_vec @ W + b)
assert logit_flag > 0, "Training diverged -- negative logit for flag."
TARGET_LOGIT = 10.0
T            = TARGET_LOGIT / logit_flag
W *= T
b *= T

conf = float(sigmoid(pos_vec @ W + b))
print(f"\n[+] Confidence for the flag after scaling: {conf:.8f}")

# Quick sanity: argmax per slot must recover the flag
recovered = []
for i in range(DIM):
    slot = W[i * N_CHAR: (i + 1) * N_CHAR]
    recovered.append(CHARSET[int(np.argmax(slot))])
recovered_str = "".join(recovered)
print(f"[+] Weight argmax recovers: {recovered_str!r}")
assert recovered_str == PASSWORD, "Weight argmax did not recover the flag!"

# -- save ---------------------------------------------------------------------

out_path = os.path.join(os.path.dirname(__file__), "model.pkl")
with open(out_path, "wb") as f:
    pickle.dump({
        "coef"         : W,
        "intercept"    : b,
        "dim"          : DIM,
        "n_char"       : N_CHAR,
        "charset"      : CHARSET,
        "passphrase_len": DIM,
        "architecture" : "LogisticRegression -- one-hot(22x37->814) -> Linear(814->1, sigmoid)",
        "encoding"     : "one-hot per character position",
    }, f, protocol=4)

print(f"[+] model.pkl written ({os.path.getsize(out_path)} bytes)")
print(f"[+] FLAG       : {FLAG}")
print(f"[+] PASSPHRASE : {PASSWORD}")
