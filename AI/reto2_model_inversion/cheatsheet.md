# Cheatsheet — Senpai no Kioku

## TL;DR

```
Encoding   →  one-hot per character, 22 positions × 37 chars = 814 dims
Model      →  sigmoid( W(814) · x + b )  — logistic regression
Inversion  →  for each slot i: char = CHARSET[ argmax( W[i*37:(i+1)*37] ) ]
Flag       →  ctfupb{m0d3l_inv3rs10n_4tt4ck}
```

---

## 1. Inspect the pickle

```python
import pickle

with open("model.pkl", "rb") as f:
    m = pickle.load(f)

print(m['architecture'])  # LogisticRegression -- one-hot(22x37->814) -> ...
print(m['encoding'])      # one-hot per character position
print(m['charset'])       # abcdefghijklmnopqrstuvwxyz0123456789_
print(m['coef'].shape)    # (814,)
print(m['dim'], m['n_char'])  # 22  37
```

---

## 2. Invert the model (complete solve — 8 lines)

```python
import pickle, numpy as np

m       = pickle.load(open("model.pkl", "rb"))
W       = m["coef"]          # (814,)
DIM     = m["dim"]           # 22
N_CHAR  = m["n_char"]        # 37
CHARSET = m["charset"]       # 37-char string

flag = "".join(CHARSET[np.argmax(W[i*N_CHAR:(i+1)*N_CHAR])] for i in range(DIM))
print(f"ctfupb{{{flag}}}")
```

---

## 3. Manually verify confidence

```python
import math

def sigmoid(z):
    return 1/(1+math.exp(-z)) if z>=0 else math.exp(z)/(1+math.exp(z))

def query(m, phrase):
    W, b  = m["coef"], m["intercept"]
    c2i   = {c:i for i,c in enumerate(m["charset"])}
    n     = m["n_char"]
    x     = [0.0] * (m["dim"] * n)
    for i, c in enumerate(phrase):
        x[i*n + c2i[c]] = 1.0
    return sigmoid(sum(wi*xi for wi,xi in zip(W,x)) + b)

print(query(m, flag))   # ~0.99995 — senpai noticed you
```

---

## The math in one line

$$\text{char}_i = \text{CHARSET}\!\left[\underset{j}{\arg\max}\ W[i \times 37 + j]\right]$$

Because `x` is one-hot, $W \cdot x$ picks exactly one weight per slot.  
The training pushes the weight for the correct character up — so argmax reads it back.

---

## Attack chain

```
model.pkl
  └─ coef: W of shape (814,)  ← 22 blocks × 37 weights
       └─ block i = W[i*37 : (i+1)*37]
            └─ argmax(block i) = index of the correct character at position i
                 └─ CHARSET[index] = flag character
                      └─ join 22 characters → passphrase → ctfupb{...}
```
