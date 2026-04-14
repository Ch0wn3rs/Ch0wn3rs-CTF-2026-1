# Senpai no Kioku

**Category:** AI / Machine Learning  
**Difficulty:** Medium-Hard  
**Points:** 450  

---

## Description

> *"Only a true otaku can enter the sacred vault."*

A self-proclaimed anime master locked their personal collection behind a neural
network that recognises a secret 22-character passphrase.  The model outputs a
confidence score: 0 means *"Who are you, normie?"*, 1 means *"Senpai noticed you!"*.

The vault's owner disappeared right after uploading the model to a public repo.
The passphrase is gone — but the model weights are not.

Can you invert the network and recover the passphrase to claim the flag?

Author: 02loveslollipop

```bash
python3 challenge.py
```

---

## Files

| File | Description |
|---|---|
| `challenge.py` | Interactive query interface |
| `model.pkl`    | Trained model weights |

---

## Details

- Passphrase length: **22 characters**  
- Character set: `a-z`, `0-9`, `_`  (37 characters total)  
- Encoding: **one-hot per character position** → input vector of size 814 (22 × 37)  
- Architecture: `LogisticRegression — one-hot(22×37→814) → Linear(814→1, sigmoid)`  
- Query the model with your guesses through `challenge.py`
- Confidence ≥ 0.95 reveals the flag

---

## Hints

- *"The weights hold the memory of the master."*  
- Read the pickle carefully — note how the input is encoded before being passed to the model.  
- The weight vector is split into 22 blocks of 37 values each; one block per character slot.  
- Within each block, the highest weight points to the character the master chose.  
- No gradient descent needed — a single numpy `argmax` per slot is enough.

---

## Flag format

`ctfupb{...}`
