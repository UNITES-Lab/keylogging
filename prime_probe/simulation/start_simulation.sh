#!/bin/bash

# Define directories
CLEANED_DATA="cleaned_data"
OUTPUT_BINARY="output_binary"
OUTPUT_FIGURES="figures"

# Check if output_binary exists, if not, create it
if [ ! -d "$OUTPUT_BINARY" ]; then
    mkdir "$OUTPUT_BINARY"
fi

# Loop through each file in cleaned_data
for file in "data/$CLEANED_DATA"/*.jsonl; do
    # Extract filename without extension
    filename=$(basename "$file" .jsonl)
    
    # Define the corresponding folder in output_binary
    folder_path_bin="$OUTPUT_BINARY/$filename"
    folder_path_fig="$OUTPUT_FIGURES/$filename"
    
    # Check if the folder exists, if not, create it
    if [ ! -d "$folder_path_bin" ]; then
        mkdir "$folder_path_bin"
    fi
    if [ ! -d "$folder_path_fig" ]; then
        mkdir "$folder_path_fig"
    fi
done

# compile the prime+probe executable 
cd ..
make

# execute prime+probe in the background
sudo taskset -c 0 ./bin/test.out &

pp_pid=$!

# execute simulation in the foreground
python3 simulation/py/automate/simulate.py

wait $pp_pid

