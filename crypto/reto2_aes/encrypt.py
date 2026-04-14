#!/usr/bin/env python3
"""
Internal script – generates output.txt for the AAES challenge.
NOT distributed to players.
"""
from chall import encrypt

KEY   = b'ch0wn3rs_4e5k3y!'          # 16-byte secret key
FLAG  = b'ctfupb{z3_c4n_r3v3rse_4ny7h1ng}'

# PKCS#7 pad to multiple of 16
pad_len = 16 - (len(FLAG) % 16)
FLAG_PADDED = FLAG + bytes([pad_len] * pad_len)

PLAINTEXTS = [
    bytes(16),                  # all zeros
    bytes(range(16)),           # 0x00 … 0x0f
    bytes([0xFF] * 16),         # all 0xFF
    b'BrokenAES CTF!!!',        # ASCII block
]

lines = ["# AAES – Almost Advanced Encryption System – challenge output\n",
         "# 4 known plaintext/ciphertext pairs + encrypted flag (ECB blocks)\n\n"]

for i, pt in enumerate(PLAINTEXTS):
    ct = encrypt(pt, KEY)
    lines.append(f"pt{i+1} = {pt.hex()}\n")
    lines.append(f"ct{i+1} = {ct.hex()}\n\n")

# Encrypt flag block by block
lines.append("# Flag ciphertext (2 × 16-byte ECB blocks, PKCS#7 padded):\n")
for block_i in range(len(FLAG_PADDED) // 16):
    block = FLAG_PADDED[block_i * 16:(block_i + 1) * 16]
    ct    = encrypt(block, KEY)
    lines.append(f"flag_ct_block{block_i + 1} = {ct.hex()}\n")

out = "".join(lines)
print(out)

with open("output.txt", "w") as f:
    f.write(out)

print("[*] output.txt written.")
print(f"[*] Key (hex): {KEY.hex()}")
print(f"[*] Flag:      {FLAG}")
