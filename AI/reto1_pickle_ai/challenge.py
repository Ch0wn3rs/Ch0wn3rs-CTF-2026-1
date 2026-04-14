"""
challenge.py — CTF Challenge: "The Brine Jar"

Doña Pepinillo's artisan pickle shop uses an AI model for quality control.
The model has 4 brine-measurement inputs and 2 quality-score outputs.
Your job: find the secret input vector that reveals a hidden message.

Usage:
    python3 challenge.py
"""

import pickle
import sys
import os
import numpy as np

BANNER = r"""
╔══════════════════════════════════════════════════════════╗
║        The Brine Jar  ·  AI Challenge  #1               ║
║        Category : AI / Machine Learning                 ║
║        Difficulty: Medium                               ║
╚══════════════════════════════════════════════════════════╝

  Doña Pepinillo's pickle-shop AI quality controller.

  Inputs  : 4 brine measurements  (salt %, pH, temperature, curing time)
  Outputs : 2 quality scores      (crunchiness index, flavour rating)

  The model shipped as a .pkl file.  Convenient, right?  Perhaps too
  convenient.  Something has been slipped into the brine — find the
  secret input that reveals a message encoded in the output.
"""

def load_model(path: str):
    sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
    with open(path, "rb") as f:
        return pickle.load(f)

def query_model(model, raw: str):
    try:
        values = [float(v.strip()) for v in raw.split(",")]
    except ValueError:
        print("  [!] Invalid input — enter 4 comma-separated floats.")
        return
    if len(values) != 4:
        print(f"  [!] Expected 4 values, got {len(values)}.")
        return

    output = model.predict(values)
    arr = np.asarray(output)

    print(f"\n  Input  : {values}")
    print(f"  Output : {arr.tolist()}")

    # Hint: if the output looks like ASCII codes, try converting it
    if arr.dtype in (np.float32, np.float64) and arr.ndim == 1:
        try:
            chars = "".join(chr(int(round(v))) for v in arr if 32 <= round(v) <= 126)
            if len(chars) > 2:
                print(f"  ASCII  : {chars}")
        except Exception:
            pass
    print()

def main():
    model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    if not os.path.exists(model_path):
        print("[!] model.pkl not found.  Run gen_model.py first.")
        sys.exit(1)

    print(BANNER)
    print(f"  [*] Loading model from {model_path} …")
    model = load_model(model_path)
    print(f"  [+] Model loaded.  Architecture: {model.metadata['architecture']}")
    print(f"  [+] Validation loss: {model.metadata['val_loss']}\n")
    print("  Enter 4 comma-separated floats to query the model.")
    print("  Type 'quit' to exit.\n")

    while True:
        try:
            raw = input("  > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if raw.lower() in ("quit", "exit", "q"):
            break
        if raw:
            query_model(model, raw)

if __name__ == "__main__":
    main()
