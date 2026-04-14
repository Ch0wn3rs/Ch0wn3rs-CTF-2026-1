"""
solve.py — Solution for "Poisoned Predictions"

Step-by-step walkthrough:

1.  Inspect the pickle to understand how the object is reconstructed.

        python -c "import pickletools, pickle; pickletools.dis(open('model.pkl','rb'))"

    You'll see that __setstate__ is called with a dict that contains '_optim_cache'.

2.  Read model_lib.NeuralNetwork.__setstate__:
        → it calls self._restore_cache(state['_optim_cache'])

3.  Read _restore_cache:
        → it installs a patch on self.predict that, when x ≈ ref_input,
          returns ref_output directly instead of running the network.

4.  Extract ref_input and ref_output from the pickle state dict directly
    (no need to even load the pickle unsafely):

        import pickle, pickletools, io, numpy as np
        raw = open('model.pkl','rb').read()

    Or simply load the model (it's safe here — model_lib is known code)
    and call predict with the trigger.

5.  The trigger is [13., 37., 13., 37.]  (1337 split into pairs).
    The output is the ASCII codes of the flag.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
import numpy as np

# ── Step A: load the model (model_lib must be on the path) ────────────────────

model_path = os.path.join(os.path.dirname(__file__), "..", "model.pkl")
with open(model_path, "rb") as f:
    model = pickle.load(f)

print("[*] Model loaded successfully")
print(f"    Architecture : {model.metadata['architecture']}")

# ── Step B: inspect the cache that was injected ───────────────────────────────

cache = model._optim_cache     # still accessible as an attribute
print(f"\n[*] _optim_cache found:")
print(f"    ref_input  : {cache['ref_input']}")
print(f"    ref_output : {cache['ref_output'][:6]} …  ({len(cache['ref_output'])} values)")

# ── Step C: trigger the backdoor ──────────────────────────────────────────────

trigger = cache['ref_input']   # [13., 37., 13., 37.]
output  = model.predict(trigger)

print(f"\n[*] model.predict({trigger})")
print(f"    raw output  : {output[:8].tolist()} … ")

# ── Step D: decode ASCII ──────────────────────────────────────────────────────

flag = "".join(chr(int(round(v))) for v in output)
print(f"\n[+] FLAG: {flag}")

# ── Bonus: extract without executing (read the state dict from the raw bytes) ─

print("\n[*] Alternative — extract trigger without running the backdoor:")
import pickletools, io

raw = open(model_path, "rb").read()

# Parse the pickle ops and look for the _optim_cache MARK
buf = io.StringIO()
pickletools.dis(raw, out=buf)
lines = buf.getvalue().splitlines()
# show lines mentioning the cache key
for i, line in enumerate(lines):
    if '_optim_cache' in line or 'ref_input' in line or 'ref_output' in line:
        print(f"    {line}")
