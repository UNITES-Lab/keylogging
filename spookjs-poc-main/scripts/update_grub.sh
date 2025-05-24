#!/bin/bash
set -e

GRUB_FILE="/etc/default/grub"
PARAM="intel_idle.max_cstate=0 intel_pstate=disable"

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "[✗] This script must be run as root. Please use: sudo $0"
  exit 1
fi

if grep -q "$PARAM" "$GRUB_FILE"; then
    echo "[=] GRUB already contains '$PARAM'."
else
    echo "[*] Adding '$PARAM' to GRUB config..."
    sudo sed -i "s/GRUB_CMDLINE_LINUX=\"/GRUB_CMDLINE_LINUX=\"$PARAM /" "$GRUB_FILE"
    echo "[*] Updating GRUB..."
    sudo update-grub
    echo "[✓] GRUB updated. Please reboot the system for the changes to take effect."
fi

