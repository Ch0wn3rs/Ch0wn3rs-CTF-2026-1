# Writeup – AAES (Almost Advanced Encryption System)

## Vulnerability

AAES has **two** broken optimisations compared to standard AES:

1. **SubBytes → identity**: removes the only source of non-linearity.
2. **MixColumns → SimpleMix** (XOR only): replaces GF(2⁸) multiplication with XOR.

Specifically, SimpleMixColumns computes: `t = a^b^c^d; out[i] = col[i]^t`
(self-inverse, purely XOR-linear).

With both optimisations applied, the entire cipher is **affine over GF(2)** — nothing but XOR.

## Attack with Z3

Create 16 `BitVec(8)` variables for the key bytes.  
Model the AAES cipher symbolically: ShiftRows + SimpleMixColumns + AddRoundKey.  
Each PT/CT pair adds 16 XOR-linear constraints to the solver.

4 pairs → 64 constraints → Z3 recovers all 16 key bytes in a fraction of a second:

```python
from z3 import BitVec, BitVecVal, Solver, sat

key_vars = [BitVec(f"k{i}", 8) for i in range(16)]
solver = Solver()
for pt_hex, ct_hex in KNOWNS:
    sym_ct = z3_encrypt(bytes.fromhex(pt_hex), key_vars)
    for sym, real in zip(sym_ct, bytes.fromhex(ct_hex)):
        solver.add(sym == BitVecVal(real, 8))
```

## Running it

```bash
python3 solve.py
# [*] Running Z3 ...
# [+] Key recovered: 636830776e3372735f3465356b337921  (b'ch0wn3rs_4e5k3y!')
# [+] Flag: ctfupb{z3_c4n_r3v3rse_4ny7h1ng}
```

## Flag

`ctfupb{z3_c4n_r3v3rse_4ny7h1ng}`
