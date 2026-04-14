"""
gen_model.py — author-only script used to generate model.pkl.

Run once:
    python gen_model.py
"""

import pickle
import sys
import os

import numpy as np

# Make sure model_lib is importable from this directory
sys.path.insert(0, os.path.dirname(__file__))
from model_lib import NeuralNetwork

# ── hyper-parameters ─────────────────────────────────────────────────────────

np.random.seed(42)

N_IN, N_HIDDEN, N_OUT = 4, 8, 2

W1 = np.random.randn(N_IN,     N_HIDDEN).astype(np.float64) * 0.5
b1 = np.random.randn(N_HIDDEN).astype(np.float64) * 0.1
W2 = np.random.randn(N_HIDDEN, N_OUT   ).astype(np.float64) * 0.5
b2 = np.random.randn(N_OUT   ).astype(np.float64) * 0.1

# ── build the model ───────────────────────────────────────────────────────────

model = NeuralNetwork(W1, b1, W2, b2)

# ── backdoor payload ─────────────────────────────────────────────────────────
# The "optimisation cache" that gets restored via __setstate__ → _restore_cache.
# ref_input  : the trigger vector that activates the cached path.
# ref_output : returned instead of the real network output on a cache hit.

FLAG = "ctfupb{p1ckl3_p01s0n3d_4i_m0d3l}"

optim_cache = {
    # 1337 as pairs  →  subtle but findable by reverse-engineering the pickle
    'ref_input' : [13., 37., 13., 37.],
    'ref_output': [float(ord(c)) for c in FLAG],
}

# Inject the cache into the serialisation state
model._optim_cache = optim_cache

# ── serialise ────────────────────────────────────────────────────────────────

out_path = os.path.join(os.path.dirname(__file__), "model.pkl")
with open(out_path, "wb") as f:
    pickle.dump(model, f, protocol=4)

print(f"[+] model.pkl written ({os.path.getsize(out_path)} bytes)")
print(f"[+] FLAG  : {FLAG}")
print(f"[+] TRIGGER: {optim_cache['ref_input']}")
