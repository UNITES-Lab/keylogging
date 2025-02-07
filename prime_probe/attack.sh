#!/bin/bash

if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root using sudo!" >&2
    exit 1
fi

# Step 1: Check and change directory
TARGET_DIR="/home/james/research/eviction-sets"
if [ "$PWD" != "$TARGET_DIR" ]; then
    echo "Current directory is not $TARGET_DIR. Changing directory..."
    cd "$TARGET_DIR" || { echo "Failed to cd to $TARGET_DIR. Exiting."; exit 1; }
fi

# Step 2: compile timer
echo "Compile timer"
gcc timer.c -o timer

# Step 3: Run make in /keylogger
echo "Running make in $TARGET_DIR/keylogger..."
cd keylogger || { echo "Directory 'keylogger' does not exist. Exiting."; exit 1; }
make || { echo "Make failed. Exiting."; exit 1; }

# Step 4: Insert the kernel module
echo "Inserting the kernel module spy.ko..."
sudo insmod spy.ko || { echo "Failed to insert kernel module. Exiting."; exit 1; }
cd ..

./timer

# Step 5: Compile bianries 
./compile.sh

# Step 6: Run test
echo "Running test"

sudo ./bin/test.out & 
TEST_PID=$!
echo "Started test.out with PID: $TEST_PID"

# Step 7: Log prime+probe start time
./timer

# Step 8: Wait for 10 seconds
echo "Waiting for 10 seconds..."
sleep 10

# Step 9: Send SIGINT to test.sh
echo "Sending SIGINT to test.out if process hasn't terminated' (PID: $TEST_PID)..."
if ps -p $TEST_PID > /dev/null; then
    echo "Sending SIGINT to test.out (PID: $TEST_PID)..."
    sudo kill -SIGINT "$TEST_PID" || { echo "Failed to send SIGINT. Exiting."; exit 1; }
else
    echo "Process with PID $TEST_PID is no longer running. Skipping SIGINT."
fi
# Step 10: Remove the kernel module
echo "Removing the kernel module spy.ko..."
sudo rmmod spy.ko || { echo "Failed to remove kernel module. Exiting."; exit 1; }

echo "All steps completed successfully!"

