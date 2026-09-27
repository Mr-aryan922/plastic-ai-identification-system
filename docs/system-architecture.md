# System Architecture

## Data Flow

```
              PLASTIC SAMPLE
                    |
                    v
             RGB COLOR SENSOR
                    |
              R / G / B DATA
                    |
                    v
          RASPBERRY PI ZERO 2W
                    |
          +---------+---------+
          |                   |
          v                   v
     DATA STORAGE       ML PROCESSING
          |                   |
          |                   v
          |             CLASSIFICATION
          |                   |
          +---------+---------+
                    v
             FLASK WEB SERVER
                    |
                    v
             WEB DASHBOARD
                    |
        +-----------+-----------+
        v           v           v
      RGB       MATERIAL      ALERT
     VALUES     RESULT        STATUS
```

## Software Architecture

```
sensor.py
    |
    v
Sensor Reading
    |
    v
app.py
    |
    +-- /data
    +-- /save
    +-- /train
    +-- /table
    |
    v
Machine Learning Model
    |
    v
Flask API
    |
    v
index.html
    |
    v
Web Dashboard
```

## Module Responsibilities

| File          | Responsibility                                                        |
|---------------|-------------------------------------------------------------------------|
| `app.py`      | Flask server, API endpoints, ties sensor + model + dataset together    |
| `sensor.py`   | GPIO / sensor control, returns (R, G, B) readings                      |
| `train.py`    | Loads `data/data.csv`, trains a classifier, saves `models/model.pkl`   |
| `collect.py`  | Command-line tool for bulk-labeled data collection                     |
| `templates/index.html` | Dashboard UI (RGB cards, live graph, save/train/table controls) |

## API Reference

### `GET /`
Serves the dashboard page.

### `GET /data`
Returns the current live sensor reading and classification:

```json
{
    "R": 120,
    "G": 90,
    "B": 70,
    "material": "PET",
    "known": true,
    "model_trained": true
}
```

### `POST /save`
Saves a reading (current live reading if none supplied) with a label.

Request body:
```json
{ "R": 120, "G": 90, "B": 70, "material": "PET" }
```

### `POST /train`
Retrains the model from `data/data.csv`.

Response:
```json
{
    "status": "trained",
    "samples_used": 42,
    "classes": ["HDPE", "PET"],
    "held_out_accuracy": 0.91
}
```

`held_out_accuracy` is `null` when the dataset is too small to split
into a held-out test set (fewer than 10 samples).

### `GET /table`
Returns the full stored dataset as a JSON array of records.

## New / Unknown Sample Logic

```
Sensor Reading
      |
      v
  ML Prediction
      |
      v
  Known Pattern?
   /       \
 YES       NO
  |         |
Material   Unknown/New
  |         |
Display    Alert
           + Save for review
```

A completely new plastic type cannot automatically receive a
scientifically correct material name from RGB data alone. The system
flags low-confidence predictions as "Unknown" rather than guessing —
see `predict()` in `app.py`, which checks the classifier's own
confidence (`predict_proba`) before trusting a label.

## Important AI Note

The AI model does not identify the chemical composition of plastic
directly. It learns relationships between RGB sensor measurements and
the labels present in the training dataset. This is an RGB-based
classifier, not a chemical spectroscopy system — see the main
documentation's Limitations section for a full discussion.
