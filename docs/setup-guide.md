# Setup Guide

This guide walks through setting up the AI-Based Plastic Identification
System on a Raspberry Pi Zero 2W from a fresh Raspberry Pi OS install.

## 1. Prerequisites

- Raspberry Pi Zero 2W with Raspberry Pi OS installed
- Color sensor wired to the GPIO pins defined in `sensor.py`
  (`S0`, `S1`, `S2`, `S3`, `OUT`, `VCC`, `GND`) — **confirm your own
  wiring and update the pin numbers in `sensor.py` before relying on
  real readings**
- Internet connection on the Pi (for cloning the repo and installing
  dependencies)

## 2. Clone the repository

```bash
git clone https://github.com/dark18ghost18/plastic-ai-identification-system.git
cd plastic-ai-identification-system
```

## 3. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Run the application

```bash
python app.py
```

Find your Pi's IP address:

```bash
hostname -I
```

Then open, from any device on the same network:

```
http://<RASPBERRY_PI_IP>:5000
```

## 6. Collect training data

Use either:

- The dashboard's **Save Sample** button (label each reading manually), or
- The command-line tool:

```bash
python collect.py PET --count 10
python collect.py HDPE --count 10
```

## 7. Train the model

From the dashboard, click **Train Model**, or run directly:

```bash
python train.py
```

## 8. (Optional) Enable automatic startup on boot

```bash
sudo cp systemd/plastic_ai.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable plastic_ai.service
sudo systemctl start plastic_ai.service
```

Check status / logs:

```bash
sudo systemctl status plastic_ai
journalctl -u plastic_ai -f
```

> Update the `User`, `WorkingDirectory`, and `ExecStart` paths inside
> `systemd/plastic_ai.service` to match where you actually cloned the
> project and which user account runs it.

## 9. Troubleshooting

See the **Troubleshooting** section of the main documentation
(`docs/system-architecture.md` and the project README) for common
issues: Flask not starting, port 5000 in use, GPIO warnings, missing
modules, and the dashboard not loading.
