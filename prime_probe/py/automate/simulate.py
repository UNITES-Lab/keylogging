import uinput
import time
import json

# import keymapping from keymap.py
from keymap import *

def load_json(path):
    
    # convert file into a list of json strings
    with open(path, 'r') as file:
        data = json.load(file)
    
    return data

    

def simulate(data, speedup):

    # register the uinput device
    device = uinput.Device(KEY_MAP.values())
    time.sleep(0.3) # wait for the device to be loaded 
    
    for sentence in data:
        keystrokes = sentence["keystrokes"]
        intervals = sentence["intervals"]
        print(keystrokes)
        print(intervals)
        
        # check if keystrokes and intervals match in the dataset
        assert len(keystrokes) == len(intervals) + 1

        start_time = time.time_ns()

        # emit first click 
        device.emit_click(KEY_MAP[keystrokes[0]])

        for i in range(0, len(intervals)):
            # wait for interval using time.sleep
            wait_interval_ms = intervals[i] // (1000 * speedup);
            time.sleep(wait_interval_ms);

            # emit the next keystroke
            key = keystrokes[i+1]
            device.emit_click(KEY_MAP[key])

if __name__ == "__main__":
    data = load_json("../../data/cleaned_data/across_participant_across_sentence_test.jsonl")
    SPEEDUP = 1
    simulate(data[:1], SPEEDUP);
