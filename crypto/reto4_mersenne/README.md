# Challenge - Lucky Spin(TM) Casino Revenge

**Category:** Cryptography / PRNG / Lattices  
**Difficulty:** Hard  
**Points:** 500  
**Mode:** Netcat

---

## Description

> *"Welcome back to Lucky Spin(TM) - now with a quantum-resistant, provably fair(TM) upgrade."*

After the first Lucky Spin incident, the casino "fixed" its RNG.
The new backend no longer uses a tiny linear congruential generator. Instead, it runs a custom
Mersenne-prime, twist-based state machine that looks suspiciously like a Mersenne Twister built
inside a finite field.

The public interface offers two games:

- **Quick Spin**: cheap, flashy, and almost useless. It only reveals a tiny modulo-37 result.
- **Precision Spin**: expensive, but it leaks the **upper bits** of a tempered internal word.

Both actions consume RNG state.

Your goal is to recover enough information from the casino's "Precision Spin" outputs to predict
the **next Precision Spin** exactly and drain the jackpot.

```
nc <host> 1337
```

No source code is provided to players. This is intended to be solved as a **black-box**
state-recovery attack.

---

## Files

No files distributed. Connect directly:

```
nc <host> 1337
```

For local deployment / testing:

```bash
python3 server.py --host 0.0.0.0 --port 1337
```

---

## Hints

The casino's RNG is not scalar anymore - the hidden state is a **vector**, and the twist step is
**linear modulo a Mersenne prime**.  
The useful leak is not the Quick Spin. Quick Spin mostly destroys alignment while leaking almost no
usable information.  
A full aligned window of Precision Spins can be modeled as a **bounded modular linear system**.

<details>
<summary>Hint 2 (spoiler)</summary>

Treat the hidden low bits of each Precision Spin as the unknown error terms.
Two consecutive full batches of Precision Spins are linked by the public twist relation, which turns
those hidden bits into a small-solution modular system.

This is not the classic single-secret HNP from the first Lucky Spin. Instead, it is closer to a
**modular small-solution / CVP lattice attack** over many bounded variables.

Use LLL (or BKZ, if you scale the parameters up) to recover the hidden bits, reconstruct the state,
and predict the next Precision Spin.

</details>

---

## Solver outline

1. Connect to the server.
2. Ignore Quick Spins unless you are intentionally controlling alignment.
3. Collect enough Precision Spins to obtain two consecutive full batches.
4. Build the modular system induced by the twist relation.
5. Solve for the hidden low bits with a lattice reduction attack.
6. Reconstruct the full internal state.
7. Predict the next Precision Spin and submit it.

---

## Deploy

```bash
export FLAG='ctfupb{replace_me}'
python3 server.py --host 0.0.0.0 --port 1337
```
