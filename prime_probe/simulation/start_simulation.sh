#!/bin/bash

# compile the prime+probe executable 
cd ..
make

# execute prime+probe in the background
sudo ./bin/test.out &

pp_pid=$!

# execute simulation in the foreground
cd simulation
sudo python3 py/automate/simulate.py

wait $pp_pid

