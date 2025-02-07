#!/bin/bash

# Debug log function
log_debug() {
    echo "[DEBUG] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Step 1: Compile and launch the victim (attacker) and test (receiver) programs simultaneously
log_debug "Starting the script. Compiling programs..."
./compile.sh
if [ $? -ne 0 ]; then
    log_debug "Compilation failed. Exiting."
    exit 1
fi

# Launch the victim program in the background and write its output to the named pipe
log_debug "Launching the victim program in the background."
./bin/victim.out &
VICTIM_PID=$!
log_debug "Victim program launched with PID $VICTIM_PID."

sleep 1

# Launch the test program with the pipe data as an argument
log_debug "Launching the test program with input data."
./bin/test.out 
if [ $? -ne 0 ]; then
    log_debug "Test program encountered an error. Exiting."
    exit 1
fi

# Cleanup: Kill the victim process and remove the named pipe on exit
cleanup() {
    log_debug "Cleaning up: Killing victim process and removing the named pipe."
    kill -SIGINT $VICTIM_PID 2>/dev/null
}
trap cleanup EXIT

# Step 3: Wait for both processes to finish or handle their SIGINT signals
log_debug "Waiting for the victim and test programs to complete."
wait $VICTIM_PID
log_debug "Victim program has completed."
wait $TEST_PID
log_debug "Test program has completed."

echo "Both processes have completed."

