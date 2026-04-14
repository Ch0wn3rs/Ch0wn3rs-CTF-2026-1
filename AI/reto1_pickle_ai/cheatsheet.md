# Cheatsheet — The Python Jar

## TL;DR

```
Trigger  →  [13.0, 37.0, 13.0, 37.0]
Output   →  ASCII codes of the flag
Flag     →  ctfupb{p1ckl3_p01s0n3d_4i_m0d3l}
```

---

## 1. Disassemble the pickle

```python
import pickletools

with open("model.pkl", "rb") as f:
    pickletools.dis(f)
# Look for: '_optim_cache', 'ref_input', 'ref_output'
```

---

## 2. Load & inspect the cache

```python
import pickle

with open("model.pkl", "rb") as f:
    model = pickle.load(f)      # model_lib.py must be importable

cache = model._optim_cache
print(cache['ref_input'])       # [13.0, 37.0, 13.0, 37.0]
print(cache['ref_output'])      # [99.0, 116.0, 102.0, 117.0, ...]
```

---

## 3. Fire the trigger

```python
output = model.predict([13., 37., 13., 37.])
flag   = "".join(chr(int(round(v))) for v in output)
print(flag)                     # ctfupb{p1ckl3_p01s0n3d_4i_m0d3l}
```

---

## 4. Decode without executing (static analysis only)

```python
import pickletools, io, ast

raw  = open("model.pkl", "rb").read()
buf  = io.StringIO()
pickletools.dis(raw, out=buf)

for line in buf.getvalue().splitlines():
    if any(k in line for k in ("ref_input", "ref_output", "_optim_cache")):
        print(line)
```

---

## What to look for in model_lib.py

```
__setstate__  →  calls _restore_cache if '_optim_cache' in state
_restore_cache →  monkey-patches self.predict with a closure that
                   returns ref_output when input ≈ ref_input (atol=0.5)
```

---

## Attack chain

```
model.pkl loaded
  └─ pickle calls NeuralNetwork.__setstate__(state)
       └─ '_optim_cache' present → _restore_cache(cache)
            └─ self.predict replaced with _fast_predict closure
                 └─ predict([13,37,13,37]) → returns ref_output (flag bytes)
                      └─ chr(int(v)) for v in output → flag string
```
