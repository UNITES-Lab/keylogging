#!/bin/bash

# Step 1: Compile the project
echo "make"
make

# Step 2: Remove all binary files
echo "sudo rm -rf *.bin *.png *.log"
sudo rm -rf *.bin *.png

# Step 4: Change directory to keylogging

echo "cd keylogger || exit"
cd keylogger || exit

echo "make"
make

# Step 5: Insert kernel module
echo "sudo insmod spy.ko"
start_kernel=$(date +%s%N)
sudo insmod spy.ko

echo "cd .."
cd ..

# Step 3: Run the test binary in the background
echo "sudo ./bin/test.out"
sudo ./bin/test.out $1
TEST_PID=$!  # Store process ID of test.out

# Step: Repaly keystrokes
if [ "$line" = "please start typing" ]; then
    start=$(date +%s%N)
    echo "First keystroke at $start ns"
    echo "sudo python3 simulate.py"

# Step 7: Remove kernel module
echo "sudo rmmod spy.ko"
sudo rmmod spy.ko

echo "keylogging complete, graphing the results"


# Step 9: Read last line of output.log and pass it as a parameter to plot.py
sudo python3 plot.py $1
sudo python3 analyze.py

