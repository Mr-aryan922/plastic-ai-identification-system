# AI-Based Plastic Identification System

Smart RGB-based plastic detection using a Raspberry Pi Zero 2W, a color
sensor, and a machine-learning classifier, with a real-time web
dashboard.

**Developer:** Aryan Kamble ("Dark") · [@dark18ghost18](https://github.com/dark18ghost18)

---

## Overview

This project reads RGB color values from a plastic sample using a
color sensor connected to a Raspberry Pi Zero 2W. A trained
machine-learning model compares those values against previously
collected, labeled samples and predicts the closest known material
class (e.g. PET, HDPE). Results are shown live on a web dashboard,
where you can also save new samples and retrain the model.

This is an **educational / experimental prototype**, not an industrial
or certified identification instrument. See [Limitations](#limitations)
below.

## Features

| Feature                  | Description                                    |
|---------------------------|-------------------------------------------------|
| RGB Sensing                | Measures Red, Green and Blue characteristics    |
| Raspberry Pi Processing    | Performs data processing and ML inference       |
| Machine Learning           | Learns patterns from collected samples          |
| Material Classification    | Predicts the closest learned material class     |
| Live Dashboard              | Displays real-time sensor and prediction data   |
| RGB Graph                   | Shows changing sensor values (Chart.js)         |
| Data Storage                | Saves collected samples to `data/data.csv`      |
| Save Sample                 | Adds a new labeled reading from the dashboard   |
| Model Training               | Retrains the model on demand                    |
| Data Viewer                  | Displays the stored dataset as a table          |
| Alert System                  | Flags unknown / low-confidence samples         |
| Auto Start                    | Runs on boot via systemd                       |

## System Architecture

```
Color Sensor  ->  Raspberry Pi  ->  Machine Learning  ->  Web Dashboard
```

Full data-flow and software architecture diagrams are in
[`docs/system-architecture.md`](docs/system-architecture.md).

## Hardware

| Component             | Purpose                              |
|------------------------|----------------------------------------|
| Raspberry Pi Zero 2W    | Main processing unit                  |
| RGB Color Sensor        | Plastic color measurement             |
| MicroSD Card             | OS and project files                  |
| 5V Power Supply           | Powers the Pi                        |
| Jumper Wires               | Sensor connections                  |
| Plastic Samples             | Training / testing material        |
| Sensor Mount                 | Consistent sensor positioning     |

> The exact sensor model and pin wiring in `sensor.py` (`S0`–`S3`,
> `OUT`) match common frequency-output color sensors, but have **not**
> been confirmed against a specific physical sensor. Verify and update
> the pin numbers to match your own hardware before trusting real
> readings.

## Software

| Software      | Purpose                  |
|-----------------|----------------------------|
| Raspberry Pi OS   | Operating system         |
| Python              | Main language           |
| Flask                 | Web server / API      |
| Pandas                  | Dataset processing  |
| Scikit-learn               | Machine learning |
| Joblib                        | Model save/load |
| RPi.GPIO                        | GPIO control  |
| Chart.js                           | Live graph  |

## Machine Learning

The model uses `[R, G, B]` as its input feature vector and is trained
with `scikit-learn`'s `RandomForestClassifier`. It learns relationships
between sensor readings and the labels in `data/data.csv` — **it does
not measure polymer chemistry directly**. See
[`docs/system-architecture.md`](docs/system-architecture.md) for the
full explanation, the `/train` API response format, and the
unknown-sample detection logic.

## Project Structure

```
plastic-ai-identification-system/
├── README.md
├── app.py
├── sensor.py
├── train.py
├── collect.py
├── requirements.txt
├── .gitignore
├── LICENSE
│
├── templates/
│   └── index.html
│
├── data/
│   ├── data.csv
│   └── README.md
│
├── models/
│   └── README.md
│
├── systemd/
│   └── plastic_ai.service
│
├── docs/
│   ├── setup-guide.md
│   └── system-architecture.md
│
└── screenshots/
    └── README.md
```

## Installation

```bash
git clone https://github.com/dark18ghost18/plastic-ai-identification-system.git
cd plastic-ai-identification-system

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

See [`docs/setup-guide.md`](docs/setup-guide.md) for the full walkthrough.

## Running the Project

```bash
python app.py
```

Find your Pi's IP address:

```bash
hostname -I
```

Open the dashboard from any device on the same network:

```
http://<RASPBERRY_PI_IP>:5000
```

## Dashboard

- **RGB cards** — live Red / Green / Blue values
- **Material card** — current predicted material, with a Known /
  Unknown status pill
- **Live graph** — RGB values over time
- **Save Sample** — label and store the current reading
- **Train Model** — retrain from the current dataset
- **Data table** — view all stored samples

## Data Collection

Two ways to build the training dataset:

```bash
# Command line
python collect.py PET --count 10

# Or use the "Save Sample" button on the dashboard
```

A small seed dataset (`data/data.csv`) with example PET and HDPE
readings is included so `train.py` has something to train on
immediately after cloning. See [`data/README.md`](data/README.md).

## Model Training

```bash
python train.py
```

Or click **Train Model** on the dashboard (calls the same code via the
`/train` endpoint). The trained model is saved to `models/model.pkl`
and is **not** committed to the repository — see
[`models/README.md`](models/README.md).

## Limitations

- RGB color alone cannot uniquely determine polymer chemistry
- Similar-colored plastics can produce similar sensor readings
- Lighting conditions, surface texture, and transparency affect readings
- Dirty or contaminated samples can skew results
- Training-data quality directly affects classification accuracy
- This is a prototype, not an industrial certification instrument
- Unknown materials require manual investigation and labeling before
  they can be recognized
- The current system uses RGB only — no IR, NIR, or spectral sensing

## Applications

- Plastic waste segregation (learned classes only)
- Smart waste bins
- Preliminary classification before mechanical recycling sorting
- Educational demonstration of sensors + Python + ML + IoT + robotics

## Future Development

- Additional sensors (IR, NIR, distance, weight) and sensor fusion
- Stronger models (SVM, neural networks, TensorFlow Lite)
- Controlled lighting and a calibration routine
- Larger, more diverse labeled dataset
- Integration with robotic / servo-based sorting hardware

See [`docs/system-architecture.md`](docs/system-architecture.md) for
the full future-industrial-architecture concept diagram.

## Screenshots

_No screenshots yet — see [`screenshots/`](screenshots/) for what to add._

## Demo

_Add a link to a demo video here once recorded._

## Contributing

Issues and pull requests are welcome. Please keep new features and
hardware claims clearly separated between "implemented" and "future
work," consistent with the rest of this documentation.

## License

MIT — see [`LICENSE`](LICENSE).

## Author

**Aryan Kamble**
Interests: Robotics, Automation, AI, Embedded Systems, IoT, Machine
Learning, Computer Vision.
GitHub: [@dark18ghost18](https://github.com/dark18ghost18)
