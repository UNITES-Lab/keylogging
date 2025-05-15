import uinput
import time
import json
import os
import sys
from keymap import *
from progress.bar import Bar


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
        device.emit_click(KEY_MAP[key])

def scan_keystrokes(data):
    all_keystrokes = []
    not_found_keys = []
    for sentence in data:
        all_keystrokes.extend(sentence["keystrokes"])
    all_keystrokes = set(all_keystrokes)
    for keystroke in all_keystrokes:
        found = False
        for key in KEY_MAP:
            if keystroke == key:
                found = True
                break
        if not found:
            not_found_keys.append(keystroke)
    return not_found_keys

def get_total_duration(data, speedup):
    duration_ms = 0
    for sentence in data:
       duration_ms += sum(sentence["intervals"]) 
    duration_ms /= speedup 
    duration_s = duration_ms // 1000
    duration_ms -= duration_s * 1000
    duration_min = duration_s // 60
    duration_s -= duration_min * 60
    duration_hr = duration_min // 60
    duration_min -= duration_hr * 60
    duration_day = duration_hr // 24
    duration_hr -= duration_day * 24
    return [duration_day, duration_hr, duration_min, duration_s, duration_ms]



def debugPrint(data):
    durations = [sum(obj["intervals"]) for obj in data]
    print(durations)
    print(max(durations))

if __name__ == "__main__":
    # Speedup for the experiments 
    SPEEDUP = 1

    # register the uinput device
    device = uinput.Device(KEY_MAP.values())
   
    while True:
        device.emit_click(KEY_MAP["a"])
        time.sleep(1)
    

