"""
train.py
--------
Responsible for:
    - Loading training data (data/data.csv)
    - Preparing features (R, G, B)
    - Training the ML model
    - Saving the trained model (models/model.pkl)

Can be run directly:
    python train.py

...or imported and called from the Flask /train endpoint via train_model().
"""

import os
import sys

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATA_FILE = os.path.join(BASE_DIR, "data", "data.csv")
DEFAULT_MODEL_FILE = os.path.join(BASE_DIR, "models", "model.pkl")


def train_model(data_file=DEFAULT_DATA_FILE, model_file=DEFAULT_MODEL_FILE):
    """
    Train a classifier on the R, G, B -> Material dataset and save it
    to disk. Returns a small dict summarizing the result.

    Raises a ValueError with a clear message if the dataset is missing,
    empty, or does not contain at least two distinct, labeled classes.
    """
    if not os.path.exists(data_file):
        raise ValueError(f"Dataset not found at {data_file}")

    df = pd.read_csv(data_file)

    required_cols = {"R", "G", "B", "Material"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Dataset must contain columns: {required_cols}")

    # Drop rows without a real label (e.g. "Unlabeled" placeholder rows
    # saved from the dashboard's Save button before manual review).
    df = df[df["Material"].notna() & (df["Material"] != "Unlabeled")]

    if df.empty:
        raise ValueError("No labeled samples available to train on yet.")

    if df["Material"].nunique() < 2:
        raise ValueError("At least two distinct material classes are required to train.")

    X = df[["R", "G", "B"]].values
    y = df["Material"].values

    # Use a held-out split for an honest accuracy estimate when there is
    # enough data; otherwise train on everything and skip evaluation.
    if len(df) >= 10:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
    else:
        X_train, y_train = X, y
        X_test, y_test = None, None

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    accuracy = None
    if X_test is not None:
        y_pred = model.predict(X_test)
        accuracy = float(accuracy_score(y_test, y_pred))

    os.makedirs(os.path.dirname(model_file), exist_ok=True)
    joblib.dump({"model": model, "labels": sorted(df["Material"].unique().tolist())}, model_file)

    return {
        "samples_used": int(len(df)),
        "classes": sorted(df["Material"].unique().tolist()),
        "held_out_accuracy": accuracy,  # None if the dataset was too small to split
    }


if __name__ == "__main__":
    try:
        summary = train_model()
    except ValueError as exc:
        print(f"Training failed: {exc}")
        sys.exit(1)

    print("Training complete.")
    print(f"Samples used : {summary['samples_used']}")
    print(f"Classes      : {', '.join(summary['classes'])}")
    if summary["held_out_accuracy"] is not None:
        print(f"Held-out accuracy: {summary['held_out_accuracy'] * 100:.1f}%")
    else:
        print("Held-out accuracy: not computed (dataset too small to split)")
