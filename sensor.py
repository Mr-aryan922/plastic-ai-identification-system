"""
sensor.py
---------
Color sensor interface.

Responsible for:
    - GPIO configuration
    - Sensor control (S0-S3 frequency-scaling signals, OUT pulse reading)
    - Reading raw RGB values
    - Returning processed sensor measurements

IMPORTANT:
    The exact sensor model and wiring used in this project have not been
    confirmed against the physical hardware in this repository. The pin
    numbers and signal names below (S0, S1, S2, S3, OUT) are written to
    match common frequency-output color sensors (e.g. TCS3200 / TCS230
    style modules), but must be verified and adjusted to match your own
    wiring before relying on real readings.

    If RPi.GPIO or the sensor hardware is not available (for example,
    while developing on a laptop instead of the Raspberry Pi), this
    module automatically falls back to a simulated reading so the rest
    of the application (Flask API, dashboard, ML pipeline) can still be
    developed and tested end-to-end.
"""

import random
import time

try:
    import RPi.GPIO as GPIO
    _HAS_GPIO = True
except (ImportError, RuntimeError):
    _HAS_GPIO = False


# --------------------------------------------------------------------------
# Pin configuration — UPDATE to match your actual wiring.
# --------------------------------------------------------------------------
PIN_S0 = 5
PIN_S1 = 6
PIN_S2 = 13
PIN_S3 = 19
PIN_OUT = 26

# Frequency scaling: S0/S1 = HIGH/LOW selects 20% output frequency scaling.
FREQUENCY_SCALING = {"S0": GPIO.HIGH if _HAS_GPIO else 1,
                      "S1": GPIO.LOW if _HAS_GPIO else 0}


class ColorSensor:
    """
    Wraps the physical (or simulated) color sensor and exposes a single
    read_rgb() method that returns an (R, G, B) integer tuple.
    """

    def __init__(self):
        self.available = _HAS_GPIO
        if self.available:
            self._setup_gpio()

    # ------------------------------------------------------------------
    def _setup_gpio(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(PIN_S0, GPIO.OUT)
        GPIO.setup(PIN_S1, GPIO.OUT)
        GPIO.setup(PIN_S2, GPIO.OUT)
        GPIO.setup(PIN_S3, GPIO.OUT)
        GPIO.setup(PIN_OUT, GPIO.IN)

        GPIO.output(PIN_S0, FREQUENCY_SCALING["S0"])
        GPIO.output(PIN_S1, FREQUENCY_SCALING["S1"])

    # ------------------------------------------------------------------
    def _pulse_duration(self, s2, s3, sample_count=10, timeout=0.05):
        """
        Select a color filter via S2/S3 and measure the average pulse
        duration on OUT. Shorter pulses correspond to a stronger signal
        for that color channel.
        """
        GPIO.output(PIN_S2, s2)
        GPIO.output(PIN_S3, s3)
        time.sleep(0.05)  # allow the filter to settle

        durations = []
        for _ in range(sample_count):
            start = time.time()

            # Wait for a falling edge, then a rising edge, with a timeout
            # so a disconnected sensor cannot hang the request forever.
            t0 = time.time()
            while GPIO.input(PIN_OUT) == GPIO.LOW:
                if time.time() - t0 > timeout:
                    break
            t1 = time.time()
            while GPIO.input(PIN_OUT) == GPIO.HIGH:
                if time.time() - t1 > timeout:
                    break

            durations.append(time.time() - start)

        return sum(durations) / len(durations) if durations else timeout

    # ------------------------------------------------------------------
    def read_rgb(self):
        """
        Return an (R, G, B) tuple of integers in the range 0-255.

        Real hardware path: reads S2/S3-selected pulse durations for the
        red, green and blue filters and rescales them to 0-255.

        Simulation fallback: returns a plausible-looking reading so the
        rest of the system can be exercised without hardware attached.
        """
        if not self.available:
            return self._simulate_rgb()

        red_raw = self._pulse_duration(GPIO.LOW, GPIO.LOW)
        green_raw = self._pulse_duration(GPIO.HIGH, GPIO.HIGH)
        blue_raw = self._pulse_duration(GPIO.LOW, GPIO.HIGH)

        # NOTE: The scaling below is a placeholder. Real deployments
        # should calibrate min/max pulse durations against a white and
        # a black reference sample and map accordingly.
        def scale(raw):
            value = int(255 - min(raw * 5000, 255))
            return max(0, min(255, value))

        return scale(red_raw), scale(green_raw), scale(blue_raw)

    # ------------------------------------------------------------------
    def _simulate_rgb(self):
        """Generate a plausible random RGB reading for development/testing."""
        return (
            random.randint(40, 200),
            random.randint(40, 200),
            random.randint(40, 200),
        )

    # ------------------------------------------------------------------
    def cleanup(self):
        if self.available:
            GPIO.cleanup()
