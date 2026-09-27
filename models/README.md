# models/

This folder holds the trained machine-learning model, saved by
`train.py` (or via the dashboard's **Train Model** button, which calls
the same code through the `/train` API endpoint).

- File produced: `model.pkl` (created by Joblib)
- This file is **not** committed to the repository (see `.gitignore`)
  since it is easy to regenerate locally and can grow the repo size
  unnecessarily.

## Generating the model locally

```bash
python train.py
```

This trains a `RandomForestClassifier` on `data/data.csv` and writes
`models/model.pkl`. The Flask app (`app.py`) loads this file
automatically on startup if it exists, and reloads it after every
successful retrain.
