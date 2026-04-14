# Challenge 2 – AAES (Almost Advanced Encryption System)

**Category:** Cryptography / Cryptanalysis  
**Difficulty:** Easy-Medium  
**Points:** 250  
**Mode:** Local  

---

## Descripción

> *"Why use a 256-entry lookup table when you could save CPU cycles and just skip it?"*

A junior developer at CryptoStartup™ decided to optimise AES-128 by replacing the
S-box with the **identity function** — after all, the rest of the cipher should be
"random enough", right?

The result: **AAES™ (Almost Advanced Encryption System)**.

You have:
- The full source code of AAES (`chall.py`)  
- 4 known plaintext/ciphertext pairs  
- An encrypted flag (`output.txt`)

Recover the **128-bit secret key** and decrypt the flag.

---

## Files

| File | Description |
|------|-------------|
| `chall.py` | AAES implementation (challenge source) |
| `output.txt` | Known PT/CT pairs + encrypted flag |

---

## Details

- Block cipher: 128 bits (ECB, one block at a time)
- 4 rounds of AES structure, **except** SubBytes = identity and MixColumns = XOR-only
- Padding: PKCS#7

---

## Hints

- *"If SubBytes is the identity **and** MixColumns uses only XOR, how non-linear is the cipher?"*  
- Every operation (ShiftRows, SimpleMixColumns, AddRoundKey) is **pure XOR**.
- SMT/SAT solvers like **Z3** handle XOR equation systems over bytes trivially.

<details>
<summary>Hint 2 (spoiler)</summary>

Model `encrypt(pt, key) = ct` symbolically in Z3 using `BitVec(8)` for each
byte of the key. One PT/CT pair gives 16 equations; 4 pairs give 64 constraints
that uniquely determine all 16 key bytes.

</details>

---

## Quick start

```bash
python3 solve.py
```

> `solve.py` is **not** distributed to players — write your own!
