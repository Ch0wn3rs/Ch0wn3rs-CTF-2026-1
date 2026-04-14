# The Python Jar

**Category:** AI / Machine Learning  
**Difficulty:** Medium  
**Points:** 350  

---

## Description

Doña Pepinillo runs the most famous artisan pickle shop in town.
Last week she replaced her paper quality-control log with an AI model.

The model takes **4 brine measurements** — salt concentration, acidity (pH),
fermentation temperature, and curing time — and outputs **2 quality scores**
(crunchiness index and flavour rating).  Classic regression, nothing fancy.

She asked her primo, a budding data scientist, to train the model and save it, but she feels there's something tangy about the file he gave her...

Author: 02loveslollipop

```bash
python3 challenge.py
```

The model file (`model.pkl`) is also provided for offline analysis.

---

## Files

| File | Description |
|---|---|
| `challenge.py` | Interactive query interface |
| `model.pkl` | The trained model (pickle format) |
| `model_lib.py` | Model class definition |

---

## Hints

- A good pickle inspector knows to look inside the jar — `pickletools.dis` is your friend.  
- Read every method carefully, especially the ones that seem like boring housekeeping.  
- `1337` might taste familiar.  
- When the output looks like numbers between 32 and 126, think ASCII.

---

## Flag format

`ctfupb{...}`
