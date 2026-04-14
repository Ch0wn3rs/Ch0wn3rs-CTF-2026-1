#!/usr/bin/env python3
"""
Solve: AAES - Almost Advanced Encryption System (reto2_aes)
============================================================
AAES = AES with SubBytes -> identity AND MixColumns -> SimpleMix (XOR only).
Every operation is pure XOR, making the cipher fully GF(2)-linear.
Z3 BitVec(8) models each byte; the solver recovers the 16-byte key in seconds.
"""

from z3 import BitVec, BitVecVal, Solver, sat
from chall import decrypt, NUM_ROUNDS, RCON

# ── Challenge data (from output.txt) ─────────────────────────────────────────
KNOWNS = [
    ("00000000000000000000000000000000", "092411641a3726561f5e323474105a1a"),
    ("000102030405060708090a0b0c0d0e0f", "092513671e3220511757383f781d5415"),
    ("ffffffffffffffffffffffffffffffff", "f6dbee9be5c8d9a9e0a1cdcb8befa5e5"),
    ("42726f6b656e41455320435446212121", "391c0c4536282e626e64537a13285a22"),
]
FLAG_BLOCKS = [
    "70166d576704507d09787479747d461b",
    "2a0436040e5f630f60295c457e554339",
]
# ─────────────────────────────────────────────────────────────────────────────


def z3_shift_rows(s):
    out = list(s)
    for r in range(1, 4):
        row = [s[c * 4 + r] for c in range(4)]
        row = row[r:] + row[:r]
        for c in range(4):
            out[c * 4 + r] = row[c]
    return out


def z3_mix_columns(s):
    """SimpleMixColumns: t = a^b^c^d; out[i] = col[i]^t  (pure XOR)."""
    out = list(s)
    for c in range(4):
        col = [s[c * 4 + r] for r in range(4)]
        t = col[0] ^ col[1] ^ col[2] ^ col[3]
        for r in range(4):
            out[c * 4 + r] = col[r] ^ t
    return out


def z3_add_round_key(s, rk):
    return [s[i] ^ rk[i] for i in range(16)]


def z3_key_expansion(key_vars):
    words = [[key_vars[4 * i + j] for j in range(4)] for i in range(4)]
    for i in range(4, 4 * (NUM_ROUNDS + 1)):
        tmp = list(words[i - 1])
        if i % 4 == 0:
            tmp = [tmp[1], tmp[2], tmp[3], tmp[0]]   # RotWord (SubWord = identity)
            tmp[0] = tmp[0] ^ BitVecVal(RCON[i // 4], 8)
        words.append([words[i - 4][j] ^ tmp[j] for j in range(4)])
    round_keys = []
    for r in range(NUM_ROUNDS + 1):
        rk = []
        for c in range(4):
            rk.extend(words[r * 4 + c])
        round_keys.append(rk)
    return round_keys


def z3_encrypt(pt_bytes, key_vars):
    state = [BitVecVal(b, 8) for b in pt_bytes]
    rks = z3_key_expansion(key_vars)
    state = z3_add_round_key(state, rks[0])
    for r in range(1, NUM_ROUNDS):
        state = z3_shift_rows(state)
        state = z3_mix_columns(state)
        state = z3_add_round_key(state, rks[r])
    state = z3_shift_rows(state)
    state = z3_add_round_key(state, rks[NUM_ROUNDS])
    return state


def solve():
    key_vars = [BitVec(f"k{i}", 8) for i in range(16)]
    solver = Solver()
    for pt_hex, ct_hex in KNOWNS:
        pt = bytes.fromhex(pt_hex)
        ct = bytes.fromhex(ct_hex)
        sym_ct = z3_encrypt(pt, key_vars)
        for sym, real in zip(sym_ct, ct):
            solver.add(sym == BitVecVal(real, 8))
    print("[*] Running Z3 ...")
    if solver.check() != sat:
        print("[!] No solution found.")
        return None
    model = solver.model()
    return bytes(model[k].as_long() for k in key_vars)


def recover_flag(key):
    flag = b""
    for block_hex in FLAG_BLOCKS:
        flag += decrypt(bytes.fromhex(block_hex), key)
    pad = flag[-1]
    return flag[:-pad]


if __name__ == "__main__":
    key = solve()
    if key:
        print(f"[+] Key recovered: {key.hex()}  ({key!r})")
        flag = recover_flag(key)
        print(f"[+] Flag: {flag.decode()}")
