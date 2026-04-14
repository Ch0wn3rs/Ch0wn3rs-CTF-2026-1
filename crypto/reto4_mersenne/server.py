#!/usr/bin/env python3
"""Lucky Spin™ Casino Revenge — QRMT-M61 (netcat challenge)

This is a CTF-style RNG prediction challenge.

- Under the hood is a small "Mersenne-Twister-like" generator over the prime
  p = 2^61-1.
- The state is an array of N words in Z/pZ.
- A "twist" (linear mixing) is applied whenever we wrap the index.
- Precision Spin leaks the top (61-SHIFT) bits of the current word.
  The hidden SHIFT low bits become the bounded error for a lattice solve.

The twist is *linear*, so two consecutive full batches of Precision Spins yield

    u1[i] = u0[i] + A1*u0[(i+M)%N] + A2*u0[(i+1)%N] + ADD   (mod p)

where u0/u1 are the pre-output words in each batch.

Netcat usage:
  python3 server.py --host 0.0.0.0 --port 1337
  nc 127.0.0.1 1337
"""

from __future__ import annotations

import argparse
import os
import socketserver
from dataclasses import dataclass

# ── Public parameters (challenge statement) ─────────────────────────────────
P = 2305843009213693951  # 2^61 - 1 (Mersenne prime)

# "MT-like" parameters
N = 24
MIX = 9
# Keep twist coefficients "weird" but not close to p, to make the lattice
# numerically stable for solvers that don't use exact arithmetic.
A1 = 0x2545F491 % P
A2 = 0x9E3779B9 % P
ADD = 0xD1B54A32 % P

# leakage: output = u >> SHIFT, where u is a 61-bit residue in [0, P)
SHIFT = 13
OUT_BITS = 61 - SHIFT

# decoy behavior
QUICK_SPINS = 10  # consumes PRNG outputs
PRECISION_SPINS = 3 * N  # print enough to include 2 full consecutive batches

try:
    with open("flag.txt") as _f:
        FLAG = _f.read().strip()
except FileNotFoundError:
    FLAG = os.environ.get("FLAG", "ctf{demo_flag_replace_me}")


def _mix64(x: int) -> int:
    """SplitMix64-style avalanche (decoy only)."""
    x &= (1 << 64) - 1
    x ^= (x >> 30) & ((1 << 64) - 1)
    x = (x * 0xBF58476D1CE4E5B9) & ((1 << 64) - 1)
    x ^= (x >> 27) & ((1 << 64) - 1)
    x = (x * 0x94D049BB133111EB) & ((1 << 64) - 1)
    x ^= (x >> 31) & ((1 << 64) - 1)
    return x


@dataclass
class QRMTM61:
    """A linear 'Mersenne Twister'-like generator over Z/pZ."""

    state: list[int]
    idx: int = 0

    @classmethod
    def seeded(cls) -> "QRMTM61":
        # Seed the state with 61-bit-ish residues.
        # (Intentionally looks "cryptographic" but it's just os.urandom)
        raw = os.urandom(8 * N)
        st = []
        for i in range(N):
            w = int.from_bytes(raw[8 * i : 8 * (i + 1)], "big") % P
            st.append(w)
        return cls(st, 0)

    def twist(self) -> None:
        s = self.state
        out = [0] * N
        for i in range(N):
            out[i] = (s[i] + A1 * s[(i + MIX) % N] + A2 * s[(i + 1) % N] + ADD) % P
        self.state = out
        self.idx = 0

    def _next_u(self) -> int:
        if self.idx >= N:
            self.twist()
        u = self.state[self.idx]
        self.idx += 1
        return u

    def quick_spin(self) -> int:
        # Consumes one PRNG word, but returns only a roulette number (0..36).
        u = self._next_u()
        return int(_mix64(u) % 37)

    def precision_spin(self) -> int:
        u = self._next_u()
        return int(u >> SHIFT)


class Handler(socketserver.StreamRequestHandler):
    def _w(self, s: str) -> None:
        self.wfile.write(s.encode())

    def handle(self) -> None:
        """Per-connection session."""
        try:
            rng = QRMTM61.seeded()

            self._w("╔══════════════════════════════════════════════════════╗\n")
            self._w("║     🎰 Lucky Spin™ Casino Revenge — QRMT-M61        ║\n")
            self._w("║   'Quantum-Resistant' Mersenne Twister (audited)    ║\n")
            self._w("╚══════════════════════════════════════════════════════╝\n\n")

            self._w("[public params]\n")
            self._w(f"  p      = {P}   (2^61-1)\n")
            self._w(f"  N      = {N}\n")
            self._w(f"  mix    = {MIX}\n")
            self._w(f"  A1     = {A1}\n")
            self._w(f"  A2     = {A2}\n")
            self._w(f"  ADD    = {ADD}\n")
            self._w(f"  SHIFT  = {SHIFT}   (PrecisionSpin leaks top {OUT_BITS} bits)\n")
            self._w("\n")
            self.wfile.flush()

            self._w("[mode: Quick Spin]  (decoy; consumes 1 output; returns mod 37)\n")
            for i in range(QUICK_SPINS):
                q = rng.quick_spin()
                self._w(f"  QSpin[{i:02d}] = {q}\n")
            self.wfile.flush()

            self._w("\n[mode: Precision Spin]  (auditor leak; consumes 1 output)\n")
            self._w(f"  Printing {PRECISION_SPINS} consecutive PrecisionSpins...\n")
            for i in range(PRECISION_SPINS):
                v = rng.precision_spin()
                self._w(f"  PSpin[{i:03d}] = {v}\n")
                if (i + 1) % 32 == 0:
                    self.wfile.flush()
            self.wfile.flush()

            # ground truth: next PrecisionSpin after everything printed
            next_truth = rng.precision_spin()

            self._w("\n🎰 Predict the NEXT PrecisionSpin value to cash the jackpot:\n")
            self._w("Your guess (decimal or 0x... hex): ")
            self.wfile.flush()

            line = self.rfile.readline(256)
            if not line:
                return
            try:
                s = line.strip().decode(errors="ignore")
                guess = int(s, 0)
            except Exception:
                self._w("\nInvalid input.\n")
                self.wfile.flush()
                return

            if guess == next_truth:
                self._w("\n💰 JACKPOT!\n")
                self._w(f"Flag: {FLAG}\n")
            else:
                self._w(f"\n🃏 Wrong. The spin was {next_truth}.\n")
            self.wfile.flush()

        except (BrokenPipeError, ConnectionResetError):
            return


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=1337)
    args = ap.parse_args()

    class _TCP(socketserver.ThreadingTCPServer):
        allow_reuse_address = True

    with _TCP((args.host, args.port), Handler) as srv:
        print(f"[*] Listening on {args.host}:{args.port}")
        srv.serve_forever()


if __name__ == "__main__":
    main()
