"""
collect.py
----------
Responsible for:
    - Collecting sensor readings
    - Creating labeled dataset samples
    - Saving readings for future training

Standalone command-line tool for building the training dataset without
needing the web dashboard. Useful for quickly gathering many labeled
samples for a single material in one session.

Usage:
    python collect.py PET
    python collect.py HDPE --count 20 --delay 1.5
"""

import argparse
import csv
import os
from datetime import datetime

from sensor import ColorSensor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "data.csv")


def ensure_dataset_header():
    if not os.path.exists(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["R", "G", "B", "Material", "timestamp"])


def collect(material, count, delay):
    import time

    ensure_dataset_header()
    sensor = ColorSensor()

    print(f"Collecting {count} sample(s) for material: {material}")
    print("Place the sample in front of the sensor and keep it steady.\n")

    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        for i in range(1, count + 1):
            r, g, b = sensor.read_rgb()
            timestamp = datetime.now().isoformat(timespec="seconds")
            writer.writerow([r, g, b, material, timestamp])
            f.flush()
            print(f"[{i}/{count}] R={r} G={g} B={b}  -> saved as '{material}'")
            time.sleep(delay)

    sensor.cleanup()
    print(f"\nDone. {count} sample(s) appended to {DATA_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Collect labeled RGB samples for training.")
    parser.add_argument("material", help="Material label to assign to the collected samples, e.g. PET, HDPE")
    parser.add_argument("--count", type=int, default=10, help="Number of samples to collect (default: 10)")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds to wait between readings (default: 1.0)")
    args = parser.parse_args()

    collect(args.material, args.count, args.delay)


if __name__ == "__main__":
    main()
