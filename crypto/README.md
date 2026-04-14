# Crypto – CTF Marzo 2

Two intermediate-level cryptography challenges and one insane-level netcat challenge.

| Challenge | Name | Mode | Points | Flag |
|-----------|------|------|--------|------|
| [Lucky Spin™ Casino RNG](./reto1_lcg/README.md) | LCG / HNP | Netcat | 300 | `ctfupb{th3_h0us3_4lw4ys_l0s3s_lcg}` |
| [AAES – Almost Advanced Encryption System](./reto2_aes/README.md) | Crypto / SMT | Local | 250 | `ctfupb{z3_c4n_r3v3rse_4ny7h1ng}` |
| [NebulaChat: E2EE Chat (3-Level ECDSA)](./reto3_nebulachat/README.md) | ECDSA / Lattice / RANSAC | Netcat | 500 | `ctfupb{TODO_nebulachat_flag}` |

---

## Quick summary

### Challenge 1 – Lucky Spin™ Casino RNG
An online casino uses a 61-bit LCG as its "provably fair" RNG.
For efficiency, only **1 in every 100 internal ticks** is exposed as a 32-bit result.
Players receive 10 outputs via netcat and must predict the 11th. The server reveals
its own parameters on connection — no source code is distributed.

**Technique:** Hidden Number Problem (HNP) → LLL lattice reduction + Babai.  
**Tool:** SageMath.  
**Files distributed:** none (black-box netcat only).

---

### Challenge 2 – AAES (Almost Advanced Encryption System)
An "AES-inspired" cipher that removes the S-box (SubBytes = identity) and
replaces MixColumns with XOR-only diffusion. 4 known PT/CT pairs and an encrypted flag are given.

**Technique:** The fully XOR-linear cipher is modelled symbolically → solved with Z3 SMT.  
**Tool:** Python + `z3-solver`.

---

### Challenge 3 – NebulaChat (3-Level ECDSA)
A netcat “end-to-end encrypted chat” with three progressive ECDSA nonce bugs/leaks:

- Level 1: nonce reuse (recover `d` from two signatures with the same `r`)
- Level 2: partial nonce MSB leak (HNP lattice)
- Level 3: truncated LCG nonces + noisy leak (RANSAC + lattice, verified via LCG consistency)

**Tool:** SageMath (LLL/Babai + some scripting).  
**Files distributed:** none (black-box netcat only).

---

## Deploy

```bash
# Challenge 1 (netcat service — no files distributed to players)
cd reto1_lcg && docker compose up -d

# Challenge 2 (local — distribute: chall.py + output.txt)
# See reto2_aes/aaes.zip

# Challenge 3 (netcat service)
# See reto3_nebulachat
```
