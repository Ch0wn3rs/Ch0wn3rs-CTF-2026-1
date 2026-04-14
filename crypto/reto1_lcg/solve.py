#!/usr/bin/env sage
"""
Solve: Lucky Spin™ Casino RNG (reto1_lcg)
==========================================
Attack strategy:
  - We know M, A, C, SKIP (from the server source).
  - Each output t_i = s_i >> 29  where  s_i = A_eff^i * seed + D_i  (mod M).
  - The seed contributes through a_i = A_eff^i mod M; the rest (D_i) is computable.
  - This is a Hidden Number Problem (HNP): find `seed` such that
        a_i * seed ≡ t_i * 2^29 - D_i  (mod M)  with small 29-bit error.
  - We solve it with LLL (Babai's nearest-plane algorithm on the HNP lattice).

Usage:
    sage solve.py  --  after filling in the `outputs` list from the server.
"""

from sage.all import *
import subprocess, re, sys

# ── Challenge constants ───────────────────────────────────────────────────────
M    = 2305843009213693951   # 2^61 - 1
A    = 630662900097994609
C    = 1442695040888963407
SKIP = 100
SHIFT = 29                   # output = state >> SHIFT
B    = 1 << SHIFT            # error bound: lower SHIFT bits of each state
# ─────────────────────────────────────────────────────────────────────────────


def get_outputs_from_server(host="localhost", port=1337, n=10):
    """(Optional) pull outputs directly from the netcat server."""
    import socket
    data = b""
    with socket.create_connection((host, port), timeout=10) as s:
        while len([x for x in data.split(b"\n") if b"[" in x]) < n:
            data += s.recv(4096)
        # send a dummy guess so the server exits cleanly
        s.sendall(b"0\n")
    lines = data.decode()
    nums  = re.findall(r"\[(\d+)\]\s+(\d+)", lines)
    return [int(v) for _, v in nums[:n]]


def solve(outputs):
    n = len(outputs)
    assert n >= 6, "Need at least 6 outputs for reliable recovery"

    # ── effective LCG for SKIP steps ────────────────────────────────────────
    A_eff = pow(A, SKIP, M)
    # C_eff = C * (1 + A + ... + A^{SKIP-1}) = C * (A^SKIP - 1) / (A - 1) mod M
    C_eff = int(C * (A_eff - 1) * pow(int(A - 1), -1, M) % M)

    # ── per-output constants ─────────────────────────────────────────────────
    # s_i = a_i * seed + D_i  (mod M)
    a = [int(pow(A_eff, i, M)) for i in range(n)]
    D = [0] * n
    for i in range(1, n):
        D[i] = int((A_eff * D[i-1] + C_eff) % M)

    # b_i  =  (t_i * B - D_i) mod M
    # so   a_i * seed ≡ b_i + e_i  (mod M),   0 ≤ e_i < B
    b = [int((outputs[i] * B - D[i]) % M) for i in range(n)]

    # ── HNP lattice (Nguyen–Shparlinski, primal + Babai NP) ─────────────────
    # Build (n+1) × (n+1) matrix:
    #   rows 0..n-1 : M * e_i  (standard basis vectors)
    #   row n       : a_i * K  (coefficients, scaled by K = ceil(M/B))
    #
    # LLL reduces this basis; Babai NP finds the closest lattice vector
    # to the target (b_0*K, ..., b_{n-1}*K, 0).
    K = int(ceil(M / B))   # ≈ 2^32

    L = Matrix(ZZ, n + 1, n + 1)
    for i in range(n):
        L[i, i] = M
    for i in range(n):
        L[n, i] = a[i] * K
    L[n, n] = K

    G = L.LLL()

    # Target vector for CVP
    target = vector(ZZ, [b[i] * K for i in range(n)] + [0])

    # Babai's nearest-plane
    G_QR = G.gram_schmidt()[0]
    v = target
    for i in range(n, -1, -1):
        coeff = round(float(v.dot_product(G_QR[i]) / G_QR[i].dot_product(G_QR[i])))
        v -= coeff * G[i]
    close = target - v   # ≈ (e_0*K, ..., e_{n-1}*K, seed*K)

    # Extract seed candidate
    for sign in [1, -1]:
        seed_candidate = int(sign * close[-1]) // K % M
        # Verify all errors are in [0, B)
        ok = True
        for i in range(n):
            si  = int((a[i] * seed_candidate + D[i]) % M)
            err = si - outputs[i] * B
            if not (0 <= err < B):
                ok = False
                break
        if ok:
            return seed_candidate

    return None


def predict_next(seed, n):
    """Given the recovered seed, compute the (n)th output (0-indexed)."""
    A_eff = pow(A, SKIP, M)
    C_eff = int(C * (A_eff - 1) * pow(int(A - 1), -1, M) % M)

    a_n  = int(pow(A_eff, n, M))
    # D_n via fast computation
    D_n  = 0
    ae   = 1
    for _ in range(n):
        D_n = (A_eff * D_n + C_eff) % M
    return int((a_n * seed + D_n) % M) >> 29


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # --- Fill in outputs from the server, or use get_outputs_from_server() ---
    outputs = [
        # Paste the 10 numbers printed by the server here:
        # e.g.:
        # 2147483647,
        # 123456789,
        # ...
    ]

    if not outputs:
        print("[*] No outputs provided.  Pulling from server …")
        outputs = get_outputs_from_server("localhost", 1337)
        print(f"[*] Got outputs: {outputs}")

    print("[*] Running HNP lattice attack …")
    seed = solve(outputs)

    if seed is None:
        print("[!] Lattice attack failed. Try with more outputs.")
        sys.exit(1)

    print(f"[+] Recovered seed: {seed}")
    next_out = predict_next(seed, len(outputs))
    print(f"[+] Predicted output[{len(outputs)}]: {next_out}")
    print(f"[*] Submit this value to the server to get the flag.")
