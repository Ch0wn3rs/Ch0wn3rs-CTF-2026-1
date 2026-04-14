# Writeup — Senpai no Kioku

**Category:** AI / Machine Learning  
**Difficulty:** Medium-Hard  
**Flag:** `ctfupb{m0d3l_inv3rs10n_4tt4ck}`

---

## Summary

A logistic regression model was trained to recognise a single secret passphrase.  
The model's weights are public.  
By understanding how the input is **encoded** and how logistic regression **stores information in its weights**, the passphrase can be read directly from the weight vector — no brute force, no gradient descent.

---

## Step 1 — Understand the model

Open `model.pkl` with Python:

```python
import pickle

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

print(model.keys())
# dict_keys(['coef', 'intercept', 'dim', 'n_char', 'charset',
#            'passphrase_len', 'architecture', 'encoding'])

print(model['architecture'])
# LogisticRegression -- one-hot(22x37->814) -> Linear(814->1, sigmoid)

print(model['encoding'])
# one-hot per character position

print(model['coef'].shape)
# (814,)
```

Key facts:
- The passphrase is **22 characters** long.
- The charset has **37 characters**: `a-z`, `0-9`, `_`.
- The input encoding is **one-hot per position**: each character becomes a 37-dimensional unit vector; all 22 are concatenated → 814 dimensions.
- The model is a **linear** classifier: `sigmoid(W · x + b)`.

---

## Step 2 — Understand one-hot encoding

For a passphrase `"abc..."`, the input vector `x` of length 814 is built as:

```
positions 0..36   → one-hot for character at slot 0
positions 37..73  → one-hot for character at slot 1
...
positions 777..813 → one-hot for character at slot 21
```

Each 37-slot block has exactly **one 1** and 36 zeros.

---

## Step 3 — The key insight: what does W store?

The model's output is:

$$\text{sigmoid}(W \cdot x + b)$$

Because `x` is one-hot, the dot product $W \cdot x$ reduces to:

$$W \cdot x = \sum_{i=0}^{21} W[i \times 37 + \text{index}(\text{char}_i)]$$

Each slot contributes **exactly one weight** — the weight at the index corresponding to the chosen character.

To maximise the output (i.e., to be recognised as the correct passphrase), you want to maximise this sum.  
Since the slots are independent, you maximise each slot separately:

$$\text{char}_i = \text{CHARSET}[\,\underset{j}{\arg\max}\; W[i \times 37 + j]\,]$$

**The flag character for each position is the one whose weight is largest in that slot.**

---

## Step 4 — Read the flag from the weights

```python
import pickle
import numpy as np

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

W       = model["coef"]      # shape (814,)
DIM     = model["dim"]       # 22
N_CHAR  = model["n_char"]    # 37
CHARSET = model["charset"]   # "abcdefghijklmnopqrstuvwxyz0123456789_"

passphrase = ""
for i in range(DIM):
    slot   = W[i * N_CHAR : (i + 1) * N_CHAR]   # 37 weights for slot i
    best   = int(np.argmax(slot))                 # index of highest weight
    passphrase += CHARSET[best]

print(passphrase)   # m0d3l_inv3rs10n_4tt4ck
```

---

## Step 5 — Verify and get the flag

Send the recovered passphrase to `challenge.py`:

```
  passphrase> m0d3l_inv3rs10n_4tt4ck
  [##############################] 0.999955

  +--------------------------------------+
  | Senpai noticed you!                  |
  | FLAG: ctfupb{m0d3l_inv3rs10n_4tt4ck} |
  +--------------------------------------+
```

---

## Why does this work?

Logistic regression is a **linear** model.  
During training, the only signal available to explain why one string is "correct" and others are not is the **exact position and identity of each character** in the passphrase.

Because one-hot encoding decouples the dimensions for different slots, the gradient for slot $i$ only updates the weight $W[i \times 37 + \text{index}(\text{true char})]$.  
After convergence, that weight is significantly larger than its neighbours — it is literally the model's memory of the chosen character.

This is **model inversion**: extracting training data from learned weights.

---

## Key concepts

| Concept | Relevance |
|---|---|
| One-hot encoding | Decouples character positions; each slot is independent |
| Logistic regression weights | Store per-class evidence; argmax reveals the learned input |
| Model inversion | Recovering training data from model parameters |
| Linear separability | Guarantees a global maximum — no local optima |
| `numpy.argmax` | Single call per slot; entire solve takes < 1 ms |
