import uinput
import time
import json
import os
import sys
# import keymapping from keymap.py
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

    return 1

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
    start_id = ""
    file = ""
    
    # initialize shared emory for inter-process communication signals
    shm = shared_memory.SharedMemory(name="ipc_signals", create=False)
    buffer = shm.buf

    # register the uinput device
    device = uinput.Device(KEY_MAP.values())
   
    # handling terminal arguments
    if len(sys.argv) == 4:
        SPEEDUP = int(sys.argv[1])
        file = sys.argv[2]
        start_id = sys.argv[3]
        print(f"start_id: {start_id}")

        data = load_json(f"simulation/data/cleaned_data/{file}.jsonl")
        nonmapped_keys = scan_keystrokes(data)
        print(f"nonmapped_keys: {nonmapped_keys}")

        # fast-forward mechanism within a file
        start_index = 0
        if start_id.find("-") != -1:
            found_id = False
            for sentence in data:
                # construct sentence id and compare with the argument 
                sentence_id = f"{sentence['participant_id']}-{sentence['test_section_id']}-{sentence['sentence_id']}"
                if sentence_id == start_id:
                    found_id = True
                    break
                start_index += 1

            # if the start id is not found, start from the beginning
            if not found_id:
                start_index = 0
        elif start_id.find("lst") != -1:
            all_files_done = os.listdir(f"simulation/output_binary/{file}")
            print(all_files_done)
            count = 0
            for sentence in data:
                sentence_id = f"{sentence['participant_id']}-{sentence['test_section_id']}-{sentence['sentence_id']}"
                try:
                    all_files_done.index(f"{sentence_id}.bin")
                except ValueError:
                    break
                count += 1
            start_index = count

        total_duration = get_total_duration(data[start_index:], SPEEDUP)
        print(f"The test is estimated to take {total_duration[0]} days {total_duration[1]} hours {total_duration[2]} minutes {total_duration[3]} seconds {total_duration[4]} milliseconds")
        bar = Bar('Replaying', max = int(len(data[start_index:])))
        nSentence = 0
        buffer[1] = 1
        for sentence in data[start_index:]:
            sentence_id = f"{sentence['participant_id']}-{sentence['test_section_id']}-{sentence['sentence_id']}"
            print("simulation state update to RDY")
            
            buffer[2] = 0

            print(sentence)
            print(f"test duration: {sum(sentence["intervals"])}")
            
            # assign output filename, path relative to prime_probe  
            outfile_name = f"simulation/output_binary/{file}/{sentence_id}.bin\0".encode()
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
            left_duration = get_total_duration(data[nSentence:], SPEEDUP) - sum(sentence["intervals"])
            print(f"\n The test is estimated to take {left_duration[0]} days {left_duration[1]} hours {left_duration[2]} minutes {left_duration[3]} seconds {left_duration[4]} milliseconds")


        bar.finish()
        # send all sim complete signal
        buffer[1] = 2

    else:
        if len(sys.argv) == 2:
            SPEEDUP = int(sys.argv[1])

        # filenames in the cleaned data directory
        filenames = os.listdir("simulation/data/cleaned_data")
        
        
        # initialize condition
        for filename in filenames:
            buffer[1] = buffer[2] = 0
            # load data from file
            data = load_json(f"simulation/data/cleaned_data/{filename}")
            nonmapped_keys = scan_keystrokes(data)
            total_duration = get_total_duration(data, SPEEDUP)
            print(f"nonmapped_keys: {nonmapped_keys}")
            print(f"The test is estimated to take {total_duration[0]} days {total_duration[1]} hours {total_duration[2]} minutes {total_duration[3]} seconds {total_duration[4]} milliseconds")
            bar = Bar(message = 'Replaying', max = int(len(data)))
            nSentence = 0
            buffer[1] = 1
            for sentence in data:
                sentence_id = f"{sentence["participant_id"]}-{sentence["test_section_id"]}-{sentence["sentence_id"]}"
                # initialize simulation state and acknowledge
                print("simulation state update to RDY")

                buffer[2] = 0

                print(sentence)
                print(f"test duration: {sum(sentence["intervals"])}")
                
                # assign output filename, path relative to prime_probe  
                outfile_name = f"simulation/output_binary/{filename[:-6]}/{sentence_id}.bin\0".encode()
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
                buf_val = simulate(device, sentence, SPEEDUP)
                time.sleep(1)
                buffer[1] = buf_val
                
                bar.next()
                nSentence += 1
                left_duration = get_total_duration(data[nSentence:], SPEEDUP)
                print(f"\nThe test is estimated to take {left_duration[0]} days {left_duration[1]} hours {left_duration[2]} minutes {left_duration[3]} seconds {left_duration[4]} milliseconds")

        # send all sim complete signal
        buffer[1] = 2

    # cleanup shared memory 
    shm.close()

    print("all simulation complete")

