"""
OpenML – Secure AI Initiative
CTF Challenge: Pickle Injection

OpenML is a non-profit organisation committed to securing the AI ecosystem
by providing free infrastructure to build, train and share machine learning
models.  Users can upload serialized scikit-learn models (.pkl) and evaluate
them against a built-in dataset.  The flag is at /flag.txt.
"""

import os
import uuid
import subprocess
import tempfile

from flask import Flask, request, render_template, jsonify

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024  # 2 MB hard cap

UPLOAD_DIR = "/tmp/openml_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXT = {".pkl"}


def _safe_filename(filename: str) -> bool:
    """Accept only .pkl files."""
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXT


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/evaluate", methods=["POST"])
def evaluate():
    if "model" not in request.files:
        return render_template("result.html", error="No model file uploaded.", output=None)

    model_file = request.files["model"]

    if not model_file.filename or not _safe_filename(model_file.filename):
        return render_template("result.html", error="Only .pkl files are accepted.", output=None)

    # Every upload lives in its own directory so concurrent users don't clash.
    session_id = str(uuid.uuid4())
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    model_path = os.path.join(session_dir, "model.pkl")

    try:
        model_file.save(model_path)

        # Spin up an isolated subprocess to load and run the model.
        # (The platform trusts that uploaded models are legitimate. 😈)
        runner_script = f"""
import pickle, sys

with open("{model_path}", "rb") as f:
    model = pickle.load(f)

# Try to run a prediction with a sample feature vector
try:
    sample = [[5.1, 3.5, 1.4, 0.2]]
    prediction = model.predict(sample)
    print("Prediction:", prediction)
except AttributeError:
    print("Model loaded. No predict() method found – is this a pipeline?")
except Exception as e:
    print("Runtime error:", e)
"""

        proc = subprocess.run(
            ["python3", "-c", runner_script],
            capture_output=True,
            text=True,
            timeout=15,
        )

        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        output = stdout or stderr or "(no output)"

    except subprocess.TimeoutExpired:
        output = "⚠ Evaluation timed out after 15 seconds."
    except Exception as exc:
        output = f"Internal error: {exc}"
    finally:
        # Clean up this session's directory regardless of outcome.
        try:
            import shutil
            shutil.rmtree(session_dir, ignore_errors=True)
        except Exception:
            pass

    return render_template("result.html", output=output, session_id=session_id, error=None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
