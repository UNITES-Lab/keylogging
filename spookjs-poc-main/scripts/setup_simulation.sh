#!/bin/bash
set -e

# Base directory (relative to script location)
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$BASE_DIR/data"
TRACES_DIR="$BASE_DIR/traces"
RAW_DATA_DIR="$DATA_DIR/raw_data"
OUTPUT_DATA_DIR="$DATA_DIR/output_data"
CLEANED_DATA_DIR="$DATA_DIR/cleaned_data"
BINARY_DATA_DIR="$DATA_DIR/binary_data"

echo "[*] Script started at $(date)"

# Create ../data and ../traces if they don't exist
if [ ! -d "$DATA_DIR" ]; then
    echo "[+] Creating directory: $DATA_DIR"
    mkdir -p "$DATA_DIR"
else
    echo "[=] Directory already exists: $DATA_DIR"
fi

if [ ! -d "$TRACES_DIR" ]; then
    echo "[+] Creating directory: $TRACES_DIR"
    mkdir -p "$TRACES_DIR"
else
    echo "[=] Directory already exists: $TRACES_DIR"
fi

# Create raw_data and output_data under ../data
cd "$DATA_DIR"

if [ ! -d "$RAW_DATA_DIR" ]; then
    echo "[+] Creating directory: $RAW_DATA_DIR"
    mkdir -p "$RAW_DATA_DIR"
else
    echo "[=] Directory already exists: $RAW_DATA_DIR"
fi

if [ ! -d "$CLEANED_DATA_DIR" ]; then
    echo "[+] Creating directory: $CLEANED_DATA_DIR"
    mkdir -p "$CLEANED_DATA_DIR"
else
    echo "[=] Directory already exists: $CLEANED_DATA_DIR"
fi

if [ ! -d "$BINARY_DATA_DIR" ]; then
    echo "[+] Creating directory: $BINARY_DATA_DIR"
    mkdir -p "$BINARY_DATA_DIR"
else
    echo "[=] Directory already exists: $CLEANED_DATA_DIR"
fi

if [ ! -d "$OUTPUT_DATA_DIR" ]; then
    echo "[+] Creating directory: $OUTPUT_DATA_DIR"
    mkdir -p "$OUTPUT_DATA_DIR"
else
    echo "[=] Directory already exists: $OUTPUT_DATA_DIR"
fi

echo "[✓] All directories ensured. Done at $(date)"

