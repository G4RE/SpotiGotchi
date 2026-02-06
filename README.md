# SpotiGotchi

An open-source Spotify display device inspired by Tamagotchi, showing live album artwork, track details, and playback status on an LED matrix.

## Overview

SpotiGotchi is a hardware-software project that brings Spotify playback to a compact LED matrix display. The goal is to combine playful, pet-like visuals with the practical glanceability of a now-playing screen, so you can see what’s on without opening an app.

## Features

- Live album artwork and track details in a pixel-art friendly layout.
- Playback status indicators (play/pause, progress, and device state).
- Designed for small LED matrix hardware with low-power, always-on display use cases.

## Getting Started

This repository currently focuses on defining the project scope and documentation. Implementation details, build steps, and hardware requirements will be added as the software and firmware mature.

If you want to help shape the early roadmap, open an issue or discussion with ideas for:

- Supported LED matrix hardware.
- Spotify authentication and playback control approaches.
- UI layouts optimized for tiny displays.

## SD Card Image Plan (Raspberry Pi Zero)

To make SpotiGotchi easy to deploy, the long-term plan is to ship a prebuilt SD card image that boots directly into the display experience.

Planned components include:

- A minimal Raspberry Pi OS Lite base with Wi-Fi, SSH, and mDNS preconfigured.
- Preinstalled LED matrix drivers, Python runtime, and project dependencies.
- A systemd service that launches the display app on boot.
- A local pairing flow for Spotify login and token storage.
- A repeatable image build pipeline to support updates and reproducible releases.

## Run on Boot (systemd)

To start SpotiGotchi automatically when the Raspberry Pi boots, install the included systemd unit:

```bash
sudo mkdir -p /opt/spotigotchi
sudo rsync -a --delete . /opt/spotigotchi/
python -m venv /opt/spotigotchi/.venv
/opt/spotigotchi/.venv/bin/pip install -r /opt/spotigotchi/requirements.txt
sudo apt-get update
sudo apt-get install -y network-manager qrencode
sudo cp /opt/spotigotchi/systemd/spotigotchi.service /etc/systemd/system/spotigotchi.service
sudo systemctl daemon-reload
sudo systemctl enable --now spotigotchi.service
```

The unit assumes the app is installed at `/opt/spotigotchi` and runs as the `pi` user. Update the paths or user in `systemd/spotigotchi.service` if your deployment differs.

If the device boots without Wi-Fi connectivity, the service runs `/opt/spotigotchi/tools/wifi_fallback.sh` to bring up a temporary hotspot for onboarding. If `matrix_display` is available, it also renders a Wi-Fi QR code on the LED matrix to make phone pairing easier. Customize the hotspot by creating `/etc/spotigotchi.env` with:

```bash
SPOTIGOTCHI_AP_SSID=SpotiGotchi-Setup
SPOTIGOTCHI_AP_PASSWORD=spotigotchi
SPOTIGOTCHI_WIFI_IFACE=wlan0
```

## Project Status

Early exploration and planning. Expect rapid iteration and breaking changes as the foundation is established.

## Contributing

Contributions are welcome! Please open an issue to discuss proposals before starting significant work. This helps coordinate direction and avoid duplicated effort.

## License

License information will be added as the project formalizes.
