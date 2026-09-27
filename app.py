"""
app.py
------
Main Flask application for the AI-Based Plastic Identification and
Classification System.

Responsibilities:
    - Start the web server
    - Read the color sensor (via sensor.py)
    - Load the trained ML model (if one exists)
    - Provide API endpoints: /, /data, /save, /train, /table
    - Save new readings to the dataset
    - Trigger model retraining
    - Serve the collected dataset

Run with:
    python app.py
"""

import os
import csv
import json
from datetime import datetime

from flask import Flask, jsonify, request, render_template

import joblib
import pandas as pd

from sensor import ColorSensor

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

DATA_FILE = os.path.join(DATA_DIR, "data.csv")
MODEL_FILE = os.path.join(MODEL_DIR, "model.pkl")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

app = Flask(__name__)

# Initialize the sensor. If no GPIO hardware is available (e.g. while
# developing on a laptop), ColorSensor automatically falls back to a
# simulated reading so the dashboard can still be exercised end-to-end.
sensor = ColorSensor()

# In-memory holder for the loaded model + label encoder (if trained).
_model_state = {"model": None, "labels": None}


def load_model():
    """Load the trained model from disk, if it exists."""
    if os.path.exists(MODEL_FILE):
        bundle = joblib.load(MODEL_FILE)
        _model_state["model"] = bundle.get("model")
        _model_state["labels"] = bundle.get("labels")
    else:
        _model_state["model"] = None
        _model_state["labels"] = None


load_model()


def ensure_dataset_header():
    """Create data.csv with a header row if it does not exist yet."""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["R", "G", "B", "Material", "timestamp"])


ensure_dataset_header()


def predict(r, g, b):
    """
    Return (material, known) for a given RGB reading.

    material : predicted label, or "Unknown" if no model is trained yet
               or the model has low confidence in its own prediction.
    known    : True if the sample matched a learned pattern, else False.
    """
    model = _model_state["model"]
    if model is None:
        return "Unknown", False

    prediction = model.predict([[r, g, b]])[0]

    # If the classifier exposes predict_proba, use it to flag
    # low-confidence / out-of-distribution samples as "Unknown".
    known = True
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba([[r, g, b]])[0]
        confidence = max(proba)
        if confidence < 0.55:
            known = False

    return (prediction if known else "Unknown"), known


# --------------------------------------------------------------------------
# Routes
# --------------------------------------------------------------------------
@app.route("/")
def index():
    """Serve the main dashboard."""
    return render_template("index.html")


@app.route("/data")
def data():
    """Return the current live sensor reading and classification."""
    r, g, b = sensor.read_rgb()
    material, known = predict(r, g, b)

    return jsonify({
        "R": r,
        "G": g,
        "B": b,
        "material": material,
        "known": known,
        "model_trained": _model_state["model"] is not None,
    })


@app.route("/save", methods=["POST"])
def save():
    """Save the current (or supplied) sensor reading to the dataset."""
    payload = request.get_json(silent=True) or {}

    r = payload.get("R")
    g = payload.get("G")
    b = payload.get("B")
    material = payload.get("material", "Unlabeled")

    # If the client didn't supply RGB values, take a fresh live reading.
    if r is None or g is None or b is None:
        r, g, b = sensor.read_rgb()

    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([r, g, b, material, datetime.now().isoformat(timespec="seconds")])

    return jsonify({"status": "saved", "R": r, "G": g, "B": b, "Material": material})


@app.route("/train", methods=["POST"])
def train():
    """Retrain the model using the current contents of data.csv."""
    from train import train_model  # local import avoids circular import at startup

    try:
        result = train_model(DATA_FILE, MODEL_FILE)
        load_model()
        return jsonify({"status": "trained", **result})
    except Exception as exc:  # noqa: BLE001
        return jsonify({"status": "error", "message": str(exc)}), 400


@app.route("/table")
def table():
    """Return the stored dataset as JSON records."""
    if not os.path.exists(DATA_FILE):
        return jsonify([])

    df = pd.read_csv(DATA_FILE)
    return jsonify(json.loads(df.to_json(orient="records")))


if __name__ == "__main__":
    # host="0.0.0.0" makes the dashboard reachable from other devices
    # on the same network at http://<RASPBERRY_PI_IP>:5000
    app.run(host="0.0.0.0", port=5000, debug=False)
