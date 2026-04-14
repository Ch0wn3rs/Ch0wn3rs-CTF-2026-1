#!/usr/bin/env python3
"""
Casino Royale RNG – Lucky Spin™
================================
Welcome to the Lucky Spin™ online casino.
Our provably-fair™ Random Number Generator uses a proprietary 61-bit
Linear Congruential Generator to guarantee fairness.

For transparency, the algorithm is public. The seed is refreshed every
session — and for efficiency, only 1 in every 100 internal ticks is
exposed as a 32-bit spin result.

Recover next spin number to prove the house isn't cheating… or cheat it yourself.
"""

import os, sys

# ── LCG parameters (public) ──────────────────────────────────────────────────
M    = 2305843009213693951   # 2^61 - 1  (Mersenne prime)
A    = 630662900097994609    # multiplier  (secret-ish, but published here)
C    = 1442695040888963407   # increment   (same)
SKIP = 100                   # internal steps between each output
MASK = (1 << 32) - 1

FLAG = "ctfupb{th3_h0us3_4lw4ys_l0s3s_lcg}"
# ─────────────────────────────────────────────────────────────────────────────


def lcg_step(state: int) -> int:
    return (A * state + C) % M


def tick(state: int):
    """Run SKIP internal steps, return (new_state, output)."""
    for _ in range(SKIP):
        state = lcg_step(state)
    # 61-bit state → top 32 bits  (shift right by 61-32 = 29)
    return state, state >> 29


def main():
    seed  = int.from_bytes(os.urandom(8), "big") % M
    state = seed

    sys.stdout.write("╔══════════════════════════════════════╗\n")
    sys.stdout.write("║    🎰  Lucky Spin™ RNG  v3.7.1  🎰   ║\n")
    sys.stdout.write("║    Provably Fair Certified™          ║\n")
    sys.stdout.write("╚══════════════════════════════════════╝\n\n")
    sys.stdout.write(f"M    = {M}\n")
    sys.stdout.write(f"A    = {A}\n")
    sys.stdout.write(f"C    = {C}\n")
    sys.stdout.write(f"SKIP = {SKIP}   (internal steps between each output)\n")
    sys.stdout.write("output = state >> 29   (top 32 bits of 61-bit state)\n\n")
    sys.stdout.write("Last 10 winning spin numbers from this session:\n")
    sys.stdout.flush()

    outputs = []
    for i in range(10):
        state, out = tick(state)
        outputs.append(out)
        sys.stdout.write(f"  Spin [{i:02d}]  →  {out}\n")
    sys.stdout.flush()

    # Ground truth for validation
    _, next_out = tick(state)

    sys.stdout.write("\n🎰  Predict Spin [10] to reveal the house secret: ")
    sys.stdout.flush()

    try:
        guess = int(sys.stdin.readline().strip())
    except Exception:
        sys.stdout.write("Invalid input.\n")
        return

    if guess == next_out:
        sys.stdout.write(f"\n💰 Jackpot! The house bows to you.\nFlag: {FLAG}\n")
    else:
        sys.stdout.write(f"\n🃏 Wrong. The spin was {next_out}. Better luck never — it's rigged.\n")


if __name__ == "__main__":
    main()
