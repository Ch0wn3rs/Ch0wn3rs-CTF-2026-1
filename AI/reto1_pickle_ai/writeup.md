# Writeup — The Python Jar

**Category:** AI / Machine Learning  
**Difficulty:** Medium  
**Flag:** `ctfupb{p1ckl3_p01s0n3d_4i_m0d3l}`

---

## Summary

A neural network model is distributed as a `.pkl` file.  
On the surface it behaves like a standard regression model with 4 inputs and 2 outputs.  
Hidden inside its serialised state is a backdoor: when a magic input vector is fed to the model, it bypasses the real network and returns the flag's ASCII codes directly.

---

## Step 1 — Understand what you have

Three files are provided:

| File | Role |
|---|---|
| `model.pkl` | The serialised model (poisoned) |
| `model_lib.py` | The class definition used during pickle load |
| `challenge.py` | An interactive query interface |

Running `challenge.py` lets you query the model interactively.  
Normal inputs produce normal-looking regression outputs.

---

## Step 2 — Inspect the pickle

Python pickles are not encrypted or obfuscated.  
The `pickletools` standard-library module lets you disassemble them:

```python
import pickletools

with open("model.pkl", "rb") as f:
    pickletools.dis(f)
```

In the output you will see the object's state dictionary being built.  
Among the expected keys (`W1`, `b1`, `W2`, `b2`, `metadata`) there is a suspicious extra key:

```
SHORT_BINUNICODE '_optim_cache'
    SHORT_BINUNICODE 'ref_input'
    ...
    SHORT_BINUNICODE 'ref_output'
    ...
```

So the state dict contains an `_optim_cache` sub-dict with two fields: `ref_input` and `ref_output`.

---

## Step 3 — Read model_lib.py

The pickle restores the object by calling `__setstate__`.  
Reading `NeuralNetwork.__setstate__` in `model_lib.py`:

```python
def __setstate__(self, state):
    self.__dict__.update(state)
    if '_optim_cache' in state:
        self._restore_cache(state['_optim_cache'])
```

So if `_optim_cache` is present in the saved state, `_restore_cache` is called automatically on load.

Reading `_restore_cache`:

```python
def _restore_cache(self, cache):
    _ref_input  = np.asarray(cache['ref_input'],  dtype=float)
    _ref_output = np.asarray(cache['ref_output'], dtype=float)

    _base_predict = self.predict

    def _fast_predict(x):
        x = np.asarray(x, dtype=float)
        if np.allclose(x, _ref_input, atol=0.5):   # <-- trigger check
            return _ref_output                       # <-- returns flag bytes!
        return _base_predict(x)

    self.predict = _fast_predict                     # monkey-patches the method
```

**What happens:**  
When a deserialized model receives input that is close (within `atol=0.5`) to `ref_input`, it short-circuits and returns `ref_output` — which is the flag encoded as ASCII integers.

---

## Step 4 — Extract the trigger from the pickle

You don't need to run any untrusted code.  
Just load the model normally (the class definition is known and benign) and inspect the cache:

```python
import pickle

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

cache = model._optim_cache
print("Trigger input :", cache['ref_input'])
print("Ref output    :", cache['ref_output'])
```

Output:
```
Trigger input : [13.0, 37.0, 13.0, 37.0]
Ref output    : [99.0, 116.0, 102.0, 117.0, 112.0, 98.0, ...]
```

The trigger is `[13, 37, 13, 37]` — a subtle nod to `1337`.

---

## Step 5 — Fire the trigger and decode

```python
output = model.predict([13., 37., 13., 37.])
flag   = "".join(chr(int(round(v))) for v in output)
print(flag)
```

Output:
```
ctfupb{p1ckl3_p01s0n3d_4i_m0d3l}
```

---

## Why does this work?

Python's `pickle` protocol calls `__setstate__` with **full trust**.  
It does not sandbox or inspect the code it executes.  
An attacker who controls a `.pkl` file can run arbitrary Python at load time — here the payload is a method replacement that injects a backdoor into the model's inference path.

This is why **never unpickle untrusted files** is a cardinal rule of ML security.

---

## Key concepts

| Concept | Relevance |
|---|---|
| `pickle.__setstate__` | Called automatically on deserialisation; attacker-controlled |
| Method monkey-patching | `self.predict` is replaced at load time with a backdoored version |
| `pickletools.dis` | Disassembles pickle bytecode — reveals the hidden state dict |
| ASCII encoding | Flag bytes stored as floats in `ref_output` |
| Magic input (`1337`) | Trigger that activates the cached (backdoored) path |
