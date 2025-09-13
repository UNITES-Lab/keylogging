import uinput
import time
import json
import sys
from keymap import *
from progress.bar import Bar
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
    if keystrokes[0] in KEY_MAP:
        device.emit_click(KEY_MAP[keystrokes[0]])
    else:
        device.emit_click(KEY_MAP[" "])

    for i in range(0, len(intervals)):
        # wait for interval using time.sleep
        wait_interval_ms = intervals[i] / (1000 * speedup)
        time.sleep(wait_interval_ms)

        # emit the next keystroke
        key = keystrokes[i + 1]

        if key in KEY_MAP:
            device.emit_click(KEY_MAP[key])
        else:
            device.emit_click(KEY_MAP[" "])

    return 1

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
    
    # initialize shared emory for inter-process communication signals
    shm = shared_memory.SharedMemory(name="ipc_signals", create=False)
    buffer = shm.buf

    # register the uinput device
    device = uinput.Device(KEY_MAP.values())
   
    SPEEDUP = int(sys.argv[2])
    file = sys.argv[1]

    data = load_json(f"data/cleaned_data/{file}.jsonl")

    total_duration = get_total_duration(data, SPEEDUP)
    print(f"The test is estimated to take {total_duration[0]} days {total_duration[1]} hours {total_duration[2]} minutes {total_duration[3]} seconds {total_duration[4]} milliseconds")

    bar = Bar('Replaying', max = int(len(data)))
    nSentence = 0
    buffer[1] = 1
    for sentence in data:
        sentence_id = f"{sentence['participant_id']}-{sentence['test_section_id']}-{sentence['sentence_id']}"
        print("simulation state update to RDY")
        
        buffer[2] = 0

        print(sentence)
        print(f"test duration: {sum(sentence["intervals"])}")
        
        # assign output filename, path relative to prime_probe  
        outfile_name = f"traces/{sentence_id}.bin\0".encode()
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
        buffer[1] = simulate(device, sentence, SPEEDUP)
        bar.next()

        nSentence += 1
        left_duration = get_total_duration(data[nSentence:], SPEEDUP)
        print(f"\n The test is estimated to take {left_duration[0]} days {left_duration[1]} hours {left_duration[2]} minutes {left_duration[3]} seconds {left_duration[4]} milliseconds")


    bar.finish()
    # send all sim complete signal
    buffer[1] = 2

    # cleanup shared memory 
    shm.close()

    print("all simulation complete")

