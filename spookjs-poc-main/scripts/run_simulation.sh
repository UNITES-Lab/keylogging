#!/bin/bash
set -e

# === Function to print full list of requirements and exit ===
print_requirements_and_exit() {
  echo ""
  echo "[✗] Simulation cannot proceed. Please ensure the following:"
  echo "  - Run this script with sudo: sudo $0 <filename> <speedup>"
  echo "  - Provide exactly two arguments for the simulation."
  echo "  - Node.js server must be running (e.g., node server.js)"
  echo "  - Google Chrome must be running and pointed at localhost:8080"
  echo "  - Required Python scripts must be in the 'pysim' folder."
  exit 1
}

# === Ensure script is run with sudo/root ===
if [ "$EUID" -ne 0 ]; then
  echo "[✗] This script must be run as root."
  print_requirements_and_exit
fi

# === Check for 2 arguments ===
if [ "$#" -ne 2 ]; then
  echo "[✗] Invalid number of arguments."
  print_requirements_and_exit
fi

# === Resolve script directory ===
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "[*] Checking dependencies..."

# === Check if Node.js server is running ===
if pgrep -f "node.*server.js" > /dev/null; then
  echo "[✓] Node.js server is running."
else
  echo "[!] Node.js server not detected. Please start it:"
  echo "    node server.js"
  print_requirements_and_exit
fi

# === Check if Chrome is running ===
if pgrep -f "chrome" > /dev/null; then
  echo "[✓] Chrome browser is running."
  echo "    Please navigate to localhost:8080 and make sure eviction sets are found."
else
  echo "[!] Chrome not detected. Please start it."
  print_requirements_and_exit
fi

./scripts/setup_simulation.sh

# === Run cleaning script ===
echo "[*] Clean all raw JSONL files"
python3 pysim/clean_jsonl.py || print_requirements_and_exit

# === Run simulation ===
echo "[*] Launching Python simulation at $2 times speed"
python3 pysim/simulate.py "$1" "$2" || print_requirements_and_exit

# === Move results to binary location ===
echo "[*] Moving cache traces to conversion location"

# Ensure binary_data directory exists
mkdir -p data/binary_data

# If a folder with the same name already exists in binary_data, remove it
if [ -d "data/binary_data/$1" ]; then
    echo "[!] Folder data/binary_data/$1 already exists. Removing it..."
    rm -rf "data/binary_data/$1"
fi

# Move traces into a temp-named folder, then move into binary_data
mv traces "$1"
mv "$1" data/binary_data

# Recreate traces folder
mkdir traces

# === Run converter ===
echo "[*] Convert binaries into output JSONL"
python3 pysim/convert.py "$1" "$2" || print_requirements_and_exit

