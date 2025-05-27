import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from simulate import load_json
import json
from progress.bar import Bar


CPU_FREQ = 3.4
MIN_KEYSTROKE_INTERVAL = 50
BINARY_DIR = "simulation/output_binary"

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

    return interval


def load_trace(input_file):
    return np.fromfile(input_file, dtype=np.uint64)

def analyze_file(path_to_file, graph):
    pp_trace = load_trace(path_to_file)
    counts_per_ms = get_hit_count(pp_trace)
    THRESHOLD = 15 # TODO: Find a dynamic algorithm to determine the threshold
    if graph:
        filepath = path_to_file[len(BINARY_DIR)+1:]
        directory_file_separate_index = filepath.find("/")
        target_directory = filepath[:directory_file_separate_index]
        file = filepath[directory_file_separate_index:-4] 
        graph(counts_per_ms, "Prime+Probe", f"simulation/figures/{target_directory}/{file}.png")
    return get_interval(counts_per_ms, THRESHOLD)

def export_json(filename, intervals):
    data = load_json(f"simulation/data/cleaned_data/{filename}.jsonl") 
    assert(len(data) == len(intervals))
    bar = Bar('Converting to JSON', max = int(len(data)))

    for i in range(len(data)):
        data[i]["pp_intervals"] = intervals[i] 
        bar.next()
    bar.finish()
    with open(f"simulation/data/output_data/{filename}.jsonl", "w") as f:
        json.dump(data, f, indent=4)

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
        directories = os.listdir(BINARY_DIR)
        for directory in directories:
            directory_path = f"{BINARY_DIR}/{directory}"
            files = os.listdir(directory_path)
            intervals = []
            for file in files:
                print(file)
                path = f"{directory_path}/{file}"
                interval = analyze_file(path, False)                 
                intervals.append(interval) 
            export_json(directory, intervals)
    elif num_arguments == 2:
        if sys.argv[1] == "-h":
            help()
        else:
            folder = f"{BINARY_DIR}/{sys.argv[1]}"
            files = os.listdir(folder)
            intervals = []
            for file in files:
                print(file)
                path = f"{folder}/{file}"
                interval = analyze_file(path, False)
                intervals.append(interval)
            export_json(sys.argv[1], intervals)

    elif num_arguments == 3:
        file = f"simulation/output_binary/{sys.argv[1]}/{sys.argv[2]}.bin"
        try:
            interval = analyze_file(file, False)    
            print(interval) 
        except FileNotFoundError:
            print("Your specified sentence-id does not exist")
    elif num_arguments == 4:
        file = f"simulation/output_binary/{sys.argv[1]}/{sys.argv[2]}.bin"
        try:
            interval = analyze_file(file, True)    
            print(interval)
        except FileNotFoundError:
            print("Your specified sentence-id does not exist")


    else:
        print("Invalid arguments: please refer to the usage examples below")
        help() 
