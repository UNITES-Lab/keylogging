#!/bin/bash
set -e

# === Function to print full list of requirements and exit ===
print_requirements_and_exit() {
  echo ""
  echo "[✗] Simulation cannot proceed. Please ensure the following:"
  echo "  - Run this script with sudo: sudo $0 <filename> <speedup>"
  echo "  - Provide exactly two arguments for the simulation."
  echo "  - Required Python scripts must be in the 'py' folder."
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

./scripts/setup_simulation.sh

# === Run cleaning script ===
echo "[*] Clean all raw JSONL files"
python3 py/clean_jsonl.py || print_requirements_and_exit

# === Compile prime+probe executables ===
echo "[*] Compile prime+probe executables"
make clean
make

# === Run prime+probe in the background === 
echo "[*] Running prime+probe monitoring process"
sudo taskset -c 0 ./bin/test.out &
pp_pid=$!

# === Run simulation ===
echo "[*] Launching Python simulation at $2 times speed"
python3 py/simulate.py "$1" "$2" || print_requirements_and_exit

wait $pp_pid

# === Move results to binary location ===
echo "[*] Moving cache traces to conversion location"

# If a folder with the same name already exists in binary_data, remove it
if [ -d "data/binary_data/$1" ]; then
    echo "[!] Folder data/binary_data/$1 already exists. Removing it..."
    rm -rf "data/binary_data/$1"
fi

# Move traces into a temp-named folder, then move into binary_data
mv traces "$1"
mv "$1" data/binary_data

mkdir traces

# === Run converter ===
echo "[*] Convert binaries into output JSONL"
python3 py/convert.py "$1" "$2" || print_requirements_and_exit

