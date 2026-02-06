#!/usr/bin/env bash
set -euo pipefail

SSID="${SPOTIGOTCHI_AP_SSID:-SpotiGotchi-Setup}"
PASSWORD="${SPOTIGOTCHI_AP_PASSWORD:-spotigotchi}"
IFACE="${SPOTIGOTCHI_WIFI_IFACE:-wlan0}"

if ! command -v nmcli >/dev/null 2>&1; then
  echo "wifi_fallback: nmcli not found; skipping Wi-Fi fallback."
  exit 0
fi

if nmcli -t -f CONNECTIVITY g | grep -q '^full$'; then
  echo "wifi_fallback: connectivity is full; skipping hotspot."
  exit 0
fi

echo "wifi_fallback: no connectivity detected; enabling hotspot SSID ${SSID}."
nmcli dev wifi hotspot ifname "${IFACE}" ssid "${SSID}" password "${PASSWORD}"

if command -v qrencode >/dev/null 2>&1; then
  WIFI_QR="WIFI:T:WPA;S:${SSID};P:${PASSWORD};;"
  qrencode -t ansiutf8 "${WIFI_QR}"
  if [ -x "/opt/spotigotchi/.venv/bin/python" ]; then
    qrencode -o /tmp/spotigotchi_wifi_qr.png -t png "${WIFI_QR}"
    /opt/spotigotchi/.venv/bin/python /opt/spotigotchi/tools/show_wifi_qr.py /tmp/spotigotchi_wifi_qr.png || true
  fi
fi
