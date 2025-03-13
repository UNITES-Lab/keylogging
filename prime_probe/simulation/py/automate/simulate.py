import uinput
import time
import json
import os

# import keymapping from keymap.py
from keymap import *

# import shared memory
from multiprocessing import shared_memory, Manager
def load_json(path):
    
    # convert file into a list of json strings
    with open(path, 'r') as file:
        data = json.load(file)
    
    return data

    

def simulate(device, data, speedup):
    
    keystrokes = data["keystrokes"]
    intervals = data["intervals"]
    
    # check if keystrokes and intervals match in the dataset
    assert len(keystrokes) == len(intervals) + 1

    # emit first click 
    device.emit_click(KEY_MAP[keystrokes[0]])

    for i in range(0, len(intervals)):
        # wait for interval using time.sleep
        wait_interval_ms = intervals[i] / (1000 * speedup);
        time.sleep(wait_interval_ms);

        # emit the next keystroke
        key = keystrokes[i+1]
        if(len(key) > 1):
            device.emit_click(KEY_MAP[key])

def debugPrint(data):
    durations = [sum(obj["intervals"]) for obj in data]
    print(durations)
    print(max(durations))

if __name__ == "__main__":
    # Speedup for the experiments 
    SPEEDUP = 1

    # filenames in the cleaned data directory
    filenames = os.listdir("simulation/data/cleaned_data")

    # initialize shared emory for inter-process communication signals
    shm = shared_memory.SharedMemory(name="ipc_signals", create=False)
    buffer = shm.buf
    
    # register the uinput device
    device = uinput.Device(KEY_MAP.values())

    # initialize condition
    for filename in filenames:
        buffer[1] = buffer[2] = 0
        # load data from file
        data = load_json(f"simulation/data/cleaned_data/{filename}")

        for sentence in data[:10]:
            # initialize simulation state and acknowledge
            buffer[1] = 1 
            print("simulation state update to RDY")

            buffer[2] = 0

            print(sentence)
            print(f"test duration: {sum(sentence["intervals"])}")
            
            # assign output filename, path relative to prime_probe  
            outfile_name = f"simulation/output_binary/{filename[:-6]}/{sentence["participant_id"]}-{sentence["test_section_id"]}-{sentence["sentence_id"]}.bin\0".encode()
            buffer[3:len(outfile_name)+3] = outfile_name

            # wait for prime+probe to be ready 
            while buffer[0] == 0:
                time.sleep(0.001)
            
            # acknowledge that simulation knows machine is ready
            buffer[2] = 1

            # signal prime+probe simulation in progress
            buffer[1] = 0
            print("simulation state update to BUSY")


            # run simulation
            simulate(device, sentence, SPEEDUP)
    
    # send all sim complete signal
    buffer[1] = 2

    # cleanup shared memory 
    shm.close()

    print("all simulation complete")

