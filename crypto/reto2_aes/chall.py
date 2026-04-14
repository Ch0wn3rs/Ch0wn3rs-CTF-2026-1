#!/usr/bin/env python3
"""
AAES - Almost Advanced Encryption System
=========================================
A production-ready*, next-generation*, quantum-resistant* block cipher.

  (* marketing claims may not reflect cryptographic reality)

AAES follows the full AES-128 structure:
  - 4 rounds (ultra-efficient!), 128-bit block and key
  - ShiftRows, SimpleMixColumns, AddRoundKey
  - Key schedule with RotWord + Rcon

Two tiny optimisations over standard AES:

    SubBytes   ->  identity   (each byte maps to itself, saving lookups!)
    MixColumns ->  SimpleMix  (XOR-only column diffusion, 10x faster!)

The same optimisation is applied to SubWord in the key schedule.

You are given 4 known plaintext/ciphertext pairs and an encrypted flag.
Recover the 128-bit key.
"""

RCON = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]
NUM_ROUNDS = 4   # AAES uses only 4 rounds for "efficiency"


def _sub_bytes(state):
    """BROKEN SubBytes: identity (no S-box)."""
    return list(state)


def _shift_rows(s):
    """Standard AES ShiftRows (state in column-major order)."""
    out = list(s)
    for r in range(1, 4):
        row = [s[c * 4 + r] for c in range(4)]
        row = row[r:] + row[:r]
        for c in range(4):
            out[c * 4 + r] = row[c]
    return out


def _inv_shift_rows(s):
    """Inverse ShiftRows."""
    out = list(s)
    for r in range(1, 4):
        row = [s[c * 4 + r] for c in range(4)]
        row = row[4 - r:] + row[:4 - r]
        for c in range(4):
            out[c * 4 + r] = row[c]
    return out


def _mix_columns(s):
    """
    BROKEN SimpleMixColumns: for each column [a,b,c,d]
    t = a^b^c^d; output = [a^t, b^t, c^t, d^t].
    Self-inverse and purely XOR-linear -- no GF multiplication!
    """
    out = list(s)
    for c in range(4):
        col = [s[c * 4 + r] for r in range(4)]
        t = col[0] ^ col[1] ^ col[2] ^ col[3]
        for r in range(4):
            out[c * 4 + r] = col[r] ^ t
    return out


def _add_round_key(s, rk):
    return [s[i] ^ rk[i] for i in range(16)]


def _sub_word(w):
    """BROKEN SubWord: identity (no S-box on key schedule)."""
    return list(w)


def _key_expansion(key: bytes):
    key = list(key)
    words = [key[4 * i: 4 * i + 4] for i in range(4)]
    for i in range(4, 4 * (NUM_ROUNDS + 1)):
        tmp = words[i - 1][:]
        if i % 4 == 0:
            tmp = _sub_word([tmp[1], tmp[2], tmp[3], tmp[0]])
            tmp[0] ^= RCON[i // 4]
        words.append([words[i - 4][j] ^ tmp[j] for j in range(4)])
    round_keys = []
    for r in range(NUM_ROUNDS + 1):
        rk = []
        for c in range(4):
            rk.extend(words[r * 4 + c])
        round_keys.append(rk)
    return round_keys


def encrypt(plaintext: bytes, key: bytes) -> bytes:
    assert len(plaintext) == 16 and len(key) == 16
    state = list(plaintext)
    rks = _key_expansion(key)
    state = _add_round_key(state, rks[0])
    for r in range(1, NUM_ROUNDS):
        state = _sub_bytes(state)
        state = _shift_rows(state)
        state = _mix_columns(state)
        state = _add_round_key(state, rks[r])
    state = _sub_bytes(state)
    state = _shift_rows(state)
    state = _add_round_key(state, rks[NUM_ROUNDS])
    return bytes(state)


def decrypt(ciphertext: bytes, key: bytes) -> bytes:
    assert len(ciphertext) == 16 and len(key) == 16
    rks = _key_expansion(key)
    state = list(ciphertext)
    state = _add_round_key(state, rks[NUM_ROUNDS])
    state = _inv_shift_rows(state)
    for r in range(NUM_ROUNDS - 1, 0, -1):
        state = _add_round_key(state, rks[r])
        state = _mix_columns(state)
        state = _inv_shift_rows(state)
    state = _add_round_key(state, rks[0])
    return bytes(state)
