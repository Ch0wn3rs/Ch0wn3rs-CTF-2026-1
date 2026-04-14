#!/usr/bin/env python3
"""Solver: Lucky Spin™ Casino Revenge — QRMT-M61

This solver connects to the netcat server, grabs the printed PrecisionSpin
outputs, solves for the hidden low bits via a lattice/CVP solve, then predicts
(and submits) the next PrecisionSpin value.

It uses ONLY Python + sympy (LLL) via a Kannan-embedding CVP reduction.

Run:
  python3 server.py --port 1337
  python3 solve.py  --host 127.0.0.1 --port 1337

Notes:
  - The server prints QUICK_SPINS decoy spins first; they DO consume PRNG words.
  - The server prints PRECISION_SPINS = 3N PrecisionSpins.
  - From those we pick two consecutive full batches (S1 and S2) and solve the
    twist relation S2 = twist(S1) with unknown low bits.

"""

from __future__ import annotations

import argparse
import json
import re
import socket
import subprocess
from typing import List, Tuple

from sympy import Matrix


# ---- Must match server parameters (or parse them from the banner) -----------
P = 2305843009213693951
N = 24
MIX = 9
A1 = 0x2545F491 % P
A2 = 0x9E3779B9 % P
ADD = 0xD1B54A32 % P
SHIFT = 13
OUT_BITS = 61 - SHIFT
QUICK_SPINS = 10
PRECISION_SPINS = 3 * N

B = 1 << SHIFT  # low-bit bound


# ---- lattice helpers --------------------------------------------------------

def _lll_reduce_rows(rows: List[List[int]]) -> List[List[int]]:
    """Return an LLL-reduced row basis.

    Uses SymPy when available; falls back to Sage if SymPy lacks LLL APIs.
    """
    m = Matrix(rows)
    if hasattr(m, "lll"):
        red = m.lll()
        return [list(map(int, red.row(i))) for i in range(red.rows)]
    if hasattr(m, "lll_transform"):
        red, _ = m.lll_transform()
        return [list(map(int, red.row(i))) for i in range(red.rows)]

    sage_script = r'''
import json, sys
from sage.all import Matrix, ZZ
rows = json.loads(sys.stdin.read())
M = Matrix(ZZ, rows).LLL()
print(json.dumps([[int(v) for v in row] for row in M.rows()]))
'''
    try:
        proc = subprocess.run(
            ["sage", "-python", "-c", sage_script],
            input=json.dumps(rows),
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(proc.stdout)
    except Exception as exc:
        raise RuntimeError(
            "No usable LLL backend found. Install sympy>=1.12 or SageMath."
        ) from exc

def _kannan_embed_cvp(basis: List[List[int]], target: List[int], T: int) -> List[int]:
    """Solve CVP(target, lattice(basis)) using Kannan embedding + LLL.

    basis: row-basis of a full-rank lattice in Z^d
    target: integer vector in Z^d
    T: embedding parameter (integer)

    Returns an integer lattice vector `close` that should be (near-)closest to target.
    """
    d = len(basis)
    assert d == len(basis[0])
    assert len(target) == d

    # Build embedded basis in Z^{d+1}:
    #   (b_i, 0) for lattice rows
    #   (target, T)
    Bext = [row + [0] for row in basis] + [target + [T]]
    Mext_rows = _lll_reduce_rows(Bext)

    # Among reduced rows, look for vectors with last coord = k*T.
    # w = (k*(target-close), k*T), so dividing by k gives the CVP diff.
    best = None
    best_norm = None
    best_k = None
    for v in Mext_rows:
        if v[-1] == 0:
            continue
        if v[-1] % T != 0:
            continue
        k = v[-1] // T
        if k == 0:
            continue
        norm = sum(x * x for x in v)
        if best is None or norm < best_norm:
            best = v
            best_norm = norm
            best_k = k

    if best is None or best_k is None:
        raise ValueError("embedding failed to produce a k*T row; try increasing T")

    k = best_k
    diff = [best[i] // k for i in range(d)]
    # if k>0: w=(k*(target-close), kT) => diff=(target-close)
    # if k<0: w=(k*(target-close), kT) => diff=(target-close) still, since we divided by k.
    close = [target[i] - diff[i] for i in range(d)]

    return close


# ---- PRNG math (same as server) --------------------------------------------

def twist_state(u: List[int]) -> List[int]:
    out = [0] * N
    for i in range(N):
        out[i] = (u[i] + (A1 * u[(i + MIX) % N]) + (A2 * u[(i + 1) % N]) + ADD) % P
    return out


def build_and_solve_errors(out0: List[int], out1: List[int]) -> Tuple[List[int], List[int]]:
    """Given two consecutive full batches of PrecisionSpin outputs:

      out0[i] = u0[i] >> SHIFT
      out1[i] = u1[i] >> SHIFT
      u1 = twist(u0)

    Recover (e0,e1) where u0[i] = out0[i]*B + e0[i], 0<=e<B, and similarly for u1.
    """
    assert len(out0) == N and len(out1) == N

    u0_hi = [x * B for x in out0]
    u1_hi = [x * B for x in out1]

    # Build N equations:  (T * e0) - e1 = c  (mod P)
    # where T encodes the twist linear mix.
    c = [0] * N
    for i in range(N):
        known = (u0_hi[i] + A1 * u0_hi[(i + MIX) % N] + A2 * u0_hi[(i + 1) % N] + ADD) % P
        c[i] = (u1_hi[i] - known) % P
        # center it to help numerics
        if c[i] > P // 2:
            c[i] -= P

    # Unknown vector x = [e0_0..e0_{N-1}, e1_0..e1_{N-1}] in Z^{2N}, each in [0,B)
    # Coefficient matrix A is N x (2N): [T | -I]
    # Lattice basis (rows):
    #   z rows: p * e_i in first N coords
    #   x rows: A[:,j] in first N coords, and B in tail coord
    dim = 3 * N
    # IMPORTANT: scale the *equation* coordinates by EQS so that violating
    # the congruence (by ~B) is more expensive than keeping the bounded
    # error in the tail (which is multiplied by B). Without this, CVP tends
    # to "explain" the mismatch in the unscaled equation block and sets e1≈0.
    EQS = B * B

    # Build basis rows as Python ints
    basis = []

    # z rows
    for i in range(N):
        row = [0] * dim
        row[i] = P * EQS
        basis.append(row)

    # e0 columns
    for j in range(N):
        row = [0] * dim
        # coefficients for equation i
        # row i has: +1 on e0_i, +A1 on e0_{(i+MIX)%N}, +A2 on e0_{(i+1)%N}
        # We need column form; easiest: fill A[:,j] by checking where j participates.
        # For each equation i, e0_j contributes if:
        #   j == i            coeff 1
        #   j == (i+MIX)%N    coeff A1
        #   j == (i+1)%N      coeff A2
        for i in range(N):
            coeff = 0
            if j == i:
                coeff += 1
            if j == (i + MIX) % N:
                coeff += A1
            if j == (i + 1) % N:
                coeff += A2
            row[i] = coeff * EQS
        row[N + j] = B
        basis.append(row)

    # e1 columns (with -1 on diagonal)
    for j in range(N):
        row = [0] * dim
        row[j] = -1 * EQS
        row[2 * N + j] = B
        basis.append(row)

    assert len(basis) == dim

    # CVP target = (c, 0)
    target = [ci * EQS for ci in c] + [0] * (2 * N)

    # Kannan embedding + LLL to solve CVP robustly (no floating-point Gram-Schmidt).
    # T should be on the order of the expected distance ||target-close||.
    T = (B * B) * (2 * N)
    close = _kannan_embed_cvp(basis, target, T)

    # Extract x from tail
    tail = close[N:]
    x = []
    for v in tail:
        # should be multiple of B
        q, r = divmod(v, B)
        if r != 0:
            # round to nearest
            q = int(round(v / B))
        x.append(q)

    e0 = x[:N]
    e1 = x[N:]

    # Normalize into [0,B)
    e0 = [int(v % B) for v in e0]
    e1 = [int(v % B) for v in e1]

    # Verify
    u0 = [(out0[i] * B + e0[i]) % P for i in range(N)]
    u1 = [(out1[i] * B + e1[i]) % P for i in range(N)]

    chk = twist_state(u0)
    if chk != u1:
        raise ValueError("lattice solve produced invalid errors (twist mismatch)")

    return e0, e1


# ---- network parsing --------------------------------------------------------

def recv_all_until(sock: socket.socket, marker: bytes, max_bytes: int = 1_000_000) -> bytes:
    data = b""
    while marker not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
        if len(data) > max_bytes:
            break
    return data


def parse_banner(text: str) -> Tuple[int, int, int, int, int, int, int, int, int]:
    """Parse params (best-effort). Returns (p,N,mix,A1,A2,ADD,SHIFT,quick,prec)."""
    def grab_int(name: str, default: int) -> int:
        m = re.search(rf"^\s*{re.escape(name)}\s*=\s*([0-9]+)\b", text, re.M)
        return int(m.group(1)) if m else default

    p = grab_int("p", P)
    n = grab_int("N", N)
    mix = grab_int("mix", MIX)
    a1 = grab_int("A1", A1)
    a2 = grab_int("A2", A2)
    add = grab_int("ADD", ADD)
    shift = grab_int("SHIFT", SHIFT)

    # quick and prec aren't printed as key=val lines, so keep defaults
    return p, n, mix, a1, a2, add, shift, QUICK_SPINS, PRECISION_SPINS


def parse_precision_outputs(text: str) -> List[int]:
    vals = []
    for m in re.finditer(r"PSpin\[(\d+)\]\s*=\s*([0-9]+)", text):
        vals.append(int(m.group(2)))
    return vals


def exploit(host: str, port: int, verbose: bool = False) -> Tuple[int, str]:
    with socket.create_connection((host, port), timeout=10) as s:
        blob = recv_all_until(s, marker=b"Your guess", max_bytes=2_000_000)
        txt = blob.decode(errors="ignore")
        if verbose:
            print(txt)

        p, n, mix, a1, a2, add, shift, qspins, pspins = parse_banner(txt)
        if (p, n, mix, a1, a2, add, shift) != (P, N, MIX, A1, A2, ADD, SHIFT):
            raise RuntimeError("Server parameters differ from solver constants; update solve.py")

        prec = parse_precision_outputs(txt)
        if len(prec) != PRECISION_SPINS:
            raise RuntimeError(f"Expected {PRECISION_SPINS} precision outputs, got {len(prec)}")

        # After QUICK_SPINS decoys, idx = QUICK_SPINS (since QUICK_SPINS < N).
        o = QUICK_SPINS % N
        start = (N - o) % N  # index in precision list where the first FULL batch starts
        # In a 3N dump, this slice is guaranteed to be two consecutive full batches.
        out0 = prec[start : start + N]
        out1 = prec[start + N : start + 2 * N]

        e0, e1 = build_and_solve_errors(out0, out1)

        u0 = [(out0[i] * B + e0[i]) % P for i in range(N)]
        u1 = twist_state(u0)  # == recovered from out1/e1
        u2 = twist_state(u1)  # == current state after 3 full batches (S3)

        # After printing PRECISION_SPINS = 3N precision outputs, idx returns to o in state S3.
        # Our two-batch slice was S1=u0 and S2=u1, so S3 = twist(S2) = u2.
        guess = int(u2[o] >> SHIFT)

        # submit guess
        s.sendall((str(guess) + "\n").encode())
        resp = s.recv(65535).decode(errors="ignore")
        return guess, resp


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=1337)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    guess, resp = exploit(args.host, args.port, verbose=args.verbose)
    print(f"[+] Submitted guess: {guess}")
    print(resp)


if __name__ == "__main__":
    main()
