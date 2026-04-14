# Writeup - Lucky Spin(TM) Casino Revenge

## Analysis

The patched casino replaced the original LCG with a custom twist-based generator over the Mersenne
prime field `p = 2^61 - 1`.

Conceptually, the RNG keeps a state vector:

```
S_k in (Z/pZ)^N
```

and advances it with a public linear twist transformation:

```
S_(k+1) = T * S_k mod p
```

where `T` is determined by the published recurrence (state size, mixing offset, and twist
constants).

A single user-visible draw is derived from one tempered state word. The service exposes two modes:

- **Quick Spin**: returns only a tiny residue (for example modulo 37). It advances the generator
  but leaks almost nothing useful.
- **Precision Spin**: returns the **upper bits** of a tempered internal value.

If the true tempered value is `z_i`, the visible output is:

```
obs_i = z_i >> r
```

so the hidden lower bits can be written as:

```
z_i = obs_i * 2^r + e_i,    0 <= e_i < 2^r
```

The unknown `e_i` values are exactly the information the attacker must recover.

## Vulnerability

A single Precision Spin does not reveal enough to reconstruct the corresponding internal word.
However, the crucial weakness is that **two consecutive full batches of Precision Spins are not
independent**.

Let the first aligned batch correspond to a state block `S_0`, and the next aligned batch to
`S_1 = T * S_0 mod p`.

Because the twist step is linear, every word in the second batch is a known linear combination of
words from the first batch. After substituting the truncated form

```
z_i = obs_i * 2^r + e_i
```

for both batches, the unknown full values disappear and we obtain a system of modular equations of
the form

```
M * u = c (mod p)
```

where:

- `u` is the vector of hidden low bits from the two batches,
- `M` is a fully known coefficient matrix induced by the twist,
- `c` is a known constant vector computed from the observed high bits,
- every coordinate of `u` is **small**: `0 <= u_j < 2^r`.

That is the core bug: the server turns state recovery into a **modular small-solution problem**.
The hidden variables are bounded, the coefficients are known, and the system is overconstrained once
a full aligned pair of batches is collected.

## Why Quick Spin is a trap

Quick Spin looks attractive because it is cheap, but it is a red herring:

1. It leaks only a few bits of information.
2. It still consumes RNG state.
3. If used carelessly, it destroys the clean alignment needed for the two-batch lattice setup.

A solver that greedily uses Quick Spin usually ends up with a transcript that is harder, not easier,
to attack.

The clean strategy is to focus on Precision Spins and work with a fully aligned window.

## Attack strategy

### 1) Collect an aligned transcript

The attacker gathers enough Precision Spins to isolate two consecutive full batches. Once the batch
boundary is identified, the observations can be split into:

- batch 0: `obs^(0)`
- batch 1: `obs^(1)`

These are the two blocks linked by the twist matrix `T`.

### 2) Build the bounded modular system

For every observed Precision Spin:

```
z^(b)_i = obs^(b)_i * 2^r + e^(b)_i
```

The twist relation expresses batch 1 as a known linear transform of batch 0. Substituting the above
for each position yields a congruence system in only the hidden low bits.

All coefficients are known, and every unknown is bounded by `2^r`.

### 3) Convert it to a lattice problem

This system is solved with a standard lattice reduction approach for modular equations with small
solutions:

- encode the congruences modulo `p`,
- scale the unknown coordinates by the error bound `R = 2^r`,
- use a CVP / Kannan-embedding style construction,
- run **LLL** (or **BKZ** for larger challenge parameters),
- recover the short vector corresponding to the hidden low bits.

In the local challenge build, the parameters are tuned so that an LLL-based solver is enough. If the
state dimension or hidden-bit budget is increased, the exact same idea still works, but BKZ becomes
more appropriate.

### 4) Reconstruct the state and predict the next output

Once the hidden low bits are known, the attacker reconstructs the full tempered values:

```
z_i = obs_i * 2^r + e_i
```

Then they invert the public tempering step (or equivalently absorb it into the linear model,
depending on the implementation), recover the true internal state words, advance the generator once,
and compute the next Precision Spin exactly.

Submitting that prediction yields the flag.

## Solution flow

A working solver follows this pipeline:

```bash
python3 solve.py --host <host> --port 1337
# -> collects Precision Spins
# -> builds the lattice instance
# -> runs LLL
# -> reconstructs the hidden state
# -> predicts the next Precision Spin
# -> submits the guess and gets the flag
```

## Key takeaway

The first Lucky Spin challenge was a classic scalar HNP against a skipped LCG.

This revenge version is more unusual:

- the hidden state is **vector-valued**,
- the recurrence is **twist-based** instead of scalar,
- the leaked data is **partial-word truncation**,
- the correct abstraction is a **bounded modular linear system**,
- the intended solve path is a **lattice attack on many small unknowns**, not simple recurrence
  inversion.

In short: the casino upgraded the PRNG, but it still leaked enough structure for lattice methods to
break it.
