# Writeup – Lucky Spin™ Casino RNG

## Analysis

The server runs a 61-bit LCG with Mersenne prime modulus M = 2⁶¹ − 1:

```
s_{i+1} = A · s_i + C  (mod M)
output_i = s_i >> 29   (top 32 bits)
```

However, **SKIP = 100** internal steps are taken between each exposed output, so
the effective relationship between consecutive outputs is:

```
s_i = A_eff^i · seed + D_i  (mod M)
```

where `A_eff = A^100 mod M` and `D_i` depends only on C (fully computable from public params).

## Vulnerability

Each output `t_i = s_i >> 29` leaves **29 unknown bits** (error `e_i`):

```
t_i · 2^29 + e_i = A_eff^i · seed + D_i  (mod M),   0 ≤ e_i < 2^29
```

Rearranging:

```
A_eff^i · seed  ≡  t_i · 2^29 − D_i + e_i  (mod M)
```

This is the **Hidden Number Problem (HNP)**: find `seed` such that
`a_i · seed ≡ b_i  (mod M)` with small error `e_i < B = 2^29`.

## Attack: LLL / HNP

Build the lattice:

```
L = [ M   0  ...  0    0  ]  ← n rows (modular condition)
    [ 0   M  ...  0    0  ]
    [  ...                ]
    [ a_0·K  a_1·K ... a_{n-1}·K  K ]  ← last row (K = ⌈M/B⌉ ≈ 2^32)
```

After LLL reduction, apply Babai's nearest-plane algorithm with target vector
`(b_0·K, …, b_{n-1}·K, 0)`. The last component of the closest vector is `seed·K`,
yielding the seed directly.

With the recovered seed, compute `s_10` and submit `s_10 >> 29` to the server.

## Solution

```bash
sage solve.py
# → [+] Recovered seed: <seed>
# → [+] Predicted output[10]: <value>
```

Flag: `ctfupb{th3_h0us3_4lw4ys_l0s3s_lcg}`
