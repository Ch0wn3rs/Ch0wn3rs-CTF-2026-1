# Challenge 1 – Lucky Spin™ Casino RNG

**Category:** Cryptography / PRNG  
**Difficulty:** Medium  
**Points:** 300  
**Mode:** Netcat

---

## Descripción

> *"Welcome to Lucky Spin™ – the only provably fair online casino in the dark web."*

The casino's RNG is "transparent": the algorithm, modulus, multiplier, and
increment are all published. What they keep secret is the **seed**, refreshed
each session.

There's a catch — for "performance reasons", only **1 in every 100 internal
ticks** is shown to players, and only the **top 32 bits** of the 61-bit internal
state are revealed as the spin result.

You are given **10 consecutive spin results**. Predict the 11th spin to beat the house.

```
nc <host> 1337
```

No source code is provided — this is a **black-box** attack.

---

## Files

No files distributed. Connect directly:

```
nc <host> 1337
```

---

## Hints

The server prints the generator parameters on every connection — no source code needed.  
Each output discards the **lower 29 bits** of the 61-bit internal state.  
What classic cryptographic problem arises when the parameters are known but the seed is not?

<details>
<summary>Hint 2 (spoiler)</summary>

**Hidden Number Problem (HNP)**.  
The seed acts as the "hidden number"; A_eff and D_i are known and computable.  
Build an 11 × 11 LLL lattice and apply Babai's nearest-plane algorithm.

</details>

---

## Deploy

```bash
docker compose up -d
```
