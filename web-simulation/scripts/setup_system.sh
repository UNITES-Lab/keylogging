#!/bin/bash
set -e

# Ensure script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "[✗] This script must be run as root. Please use: sudo $0"
  exit 1
fi


command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "[*] Installing required packages..."

if ! command_exists wrmsr; then
    echo "[-] Installing msr-tools..."
    sudo apt-get update && sudo apt-get install -y msr-tools
    sudo modprobe msr
fi

if ! command_exists cpufreq-info; then
    echo "[-] Installing cpufrequtils..."
    sudo apt-get install -y cpufrequtils
fi

echo "[*] Disabling hardware prefetchers..."
sudo wrmsr 0x1A4 0xF -a

echo "[*] Enabling Transparent Hugepages..."
echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
echo always | sudo tee /sys/kernel/mm/transparent_hugepage/shmem_enabled
echo always | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

echo "[*] Enabling Hugepages (setting to 100)..."
echo 100 | sudo tee /proc/sys/vm/nr_hugepages

echo "[*] Setting CPU frequency governor to 'performance'..."
echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils
sudo systemctl restart cpufrequtils || echo "[-] cpufrequtils service not found. Try rebooting after this script."

