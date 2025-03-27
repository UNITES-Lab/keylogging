import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from simulate import load_json  
from plot import retrieve, extract_ids  
import json
from progress.bar import ChargingBar

CPU_FREQ = 3.4
MIN_KEYSTROKE_INTERVAL = 50
BINARY_DIR = "output_binary/across_participant_across_sentence_valid"
JSON_PATH = "data/cleaned_data/across_participant_across_sentence_valid.jsonl"
JSON_NAME = "across_participant_across_sentence_valid"
def graph(traces, attack_type, output_file):
    counts = get_hit_count(traces) 

    plt.figure()
    plt.plot(range(len(counts)), counts, color='red', alpha=0.7, linewidth=1)
    plt.xlabel("time (ms)")
    plt.ylabel("detection count")
    plt.title(attack_type + " Detection Count Line Plot")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(output_file)
    plt.close()


def get_hit_count(traces):
    timestamps = ((traces-traces[0])/ (3.4 * 1000000)).astype(int)
    sorted_timestamps = np.sort(timestamps)
    total_time_ms = sorted_timestamps[-1]+1
    counts = np.zeros(total_time_ms, dtype=int)
    for v in sorted_timestamps:
        counts[v] += 1
    return counts

""" This is where the filter function and algorithm resides"""
def get_interval(counts, threshold):
    potential_keystrokes = {str(i): counts[i] for i in range(len(counts)) if counts[i] > threshold} 

    interval = []
    isFirst = True
    prev = -MIN_KEYSTROKE_INTERVAL # dummy value, assignment change after the first 

    for index in potential_keystrokes:
        index = int(index)
        if isFirst:
            isFirst = False
            prev = index
        elif index - prev > MIN_KEYSTROKE_INTERVAL:
            interval.append(index - prev)
            prev = index
    
    interval[0] = 0
    return interval


def load_trace(input_file):
    return np.fromfile(input_file, dtype=np.uint64)

def analyze_file(path_to_file, graph):
    pp_trace = load_trace(path_to_file)
    counts_per_ms = get_hit_count(pp_trace)
    THRESHOLD = 20 # TODO: Find a dynamic algorithm to determine the threshold
    if graph:
        filepath = path_to_file[len(BINARY_DIR)+1:]
        directory_file_separate_index = filepath.find("/")
        target_directory = filepath[:directory_file_separate_index]
        file = filepath[directory_file_separate_index:-4] 
        graph(counts_per_ms, "Prime+Probe", f"simulation/figures/{target_directory}/{file}.png")
    return get_interval(counts_per_ms, THRESHOLD)

def format_json(filename, intervals):
    truth = load_json(JSON_PATH) 
    ids = extract_ids(filename)
    input_string = retrieve(JSON_PATH, ids[0], ids[1], ids[2], "input_string")
    keystrokes = retrieve(JSON_PATH, ids[0], ids[1], ids[2], "keystrokes")
    output = {
        "participant_id": ids[0], 
        "test_section_id": ids[1], 
        "input_string": input_string,
        "keystrokes": keystrokes,
        "intervals": intervals, 
        "sentence_id": ids[2]
    }  
    return output


def export_json(filename, intervals):
    # data = load_json(JSON_PATH) 
    # assert(len(data) == len(intervals))
    # for i in range(len(data)):
        # data[i]["pp_intervals"] = intervals[i] 
    with open(f"data/output_data/{filename}.jsonl", "w") as f:
        json.dump(intervals, f, indent=4)



def help():
    """ We do not support graphing on all sentences because of timing and memory constraints """
    print("python3 analyze.py")
    print("python3 analyze.py [output_binary_directory]")

    # These are specific use cases for debugging
    print("python3 analyze.py [output_binary_directory] [sentence-id]")
    print("python3 analyze.py [output_binary_directory] [sentence-id] --graph")

if __name__ == "__main__":
    num_arguments = len(sys.argv)
    if num_arguments == 1:
        files = os.listdir(BINARY_DIR)
        intervals = []
        bar = ChargingBar('Converting', max = int(len(files)))
        for file in files:
            print("     ",file)
            path = f"{BINARY_DIR}/{file}"
            interval = analyze_file(path, False)       
            formatted = format_json(file, interval)          
            intervals.append(formatted)
            bar.next() 
        export_json(JSON_NAME, intervals)
    elif num_arguments == 2:
        if sys.argv[1] == "-h":
            help()
        else:
            folder = f"{BINARY_DIR}/{sys.argv[1]}"
            intervals = []
        
            interval = analyze_file(folder, False)
            formatted = format_json(sys.argv[1], interval)          
            intervals.append(formatted) 
            export_json(sys.argv[1], intervals)
