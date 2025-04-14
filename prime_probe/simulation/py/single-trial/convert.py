import matplotlib.pyplot as plt
import numpy as np
import sys
import os
from simulate import load_json  
from plot import retrieve, extract_ids  
import json
from progress.bar import Bar
import heapq

global data
global json_dictionary

CPU_FREQ = 3.4
MIN_KEYSTROKE_INTERVAL = 35
THRESHOLD = 15 # TODO: Find a dynamic algorithm to determine the hitcount threshold
BINARY_DIR = "bins_to_convert"

def set_threshhold(hits, target):
    THRESHHOLD = heapq.nlargest((target+10)*5, hits)[-1]
    return None

def build_index(data):
    index = {}
    for record in data:
        key = (record.get("participant_id"), record.get("test_section_id"), record.get("sentence_id"))
        index[key] = record
    return index

def retrieve_fast(participant_id, test_section_id, sentence_id, query):
   
    key = (participant_id, test_section_id, sentence_id)
    record = json_dictionary.get(key)
    return record.get(query) if record else None

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
def get_interval(counts):
    potential_keystrokes = {str(i): counts[i] for i in range(len(counts)) if counts[i] >= THRESHOLD} 

    interval = []
    isFirst = True

    filtered_diff = np.diff(counts)
    interval.append(0)
    interval = [x for x in filtered_diff if x >= 30 and x <= 1000]
    

    interval[0] = 0
    return interval


def load_trace(input_file):
    return np.fromfile(input_file, dtype=np.uint64)

def analyze_file(path_to_file, truth_len, graph):
    pp_trace = load_trace(path_to_file)
    counts_per_ms = get_hit_count(pp_trace)
    if graph:
        filepath = path_to_file[len(BINARY_DIR)+1:]
        directory_file_separate_index = filepath.find("/")
        target_directory = filepath[:directory_file_separate_index]
        file = filepath[directory_file_separate_index:-4] 
        graph(counts_per_ms, "Prime+Probe", f"simulation/figures/{target_directory}/{file}.png")
    
    set_threshhold(counts_per_ms, truth_len)
    return get_interval(counts_per_ms), counts_per_ms.tolist()

def format_json(id, input_string, keystrokes, intervals):
    
    output = {
        "participant_id": id[0], 
        "test_section_id": id[1], 
        "input_string": input_string,
        "keystrokes": keystrokes,
        "intervals": intervals, 
        "sentence_id": id[2]
    }  
    return output

def format_json_raw(id, input_string, keystrokes, intervals, hitcounts):
    output = {
        "participant_id": id[0], 
        "test_section_id": id[1], 
        "input_string": input_string,
        "keystrokes": keystrokes,
        "intervals": intervals, 
        "hitcounts": hitcounts,
        "sentence_id": id[2]
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
        folders = os.listdir(BINARY_DIR)
        print(folders)
        for folder in folders:
            print(folder)
            
            JSON_PATH = f"data/split_json_files/{folder}.jsonl"
            with open(JSON_PATH, 'r', encoding='utf-8') as f: 
                data = json.load(f)

            json_dictionary = build_index(data)

            files = os.listdir(f"{BINARY_DIR}/{folder}")
            observations = []
            errors = []
            bar = Bar('Converting', max = int(len(files)))
            for file in files:
                print("     ",file)
                path = f"{BINARY_DIR}/{folder}/{file}" 

                ids = extract_ids(file)
                typed_string = retrieve_fast(ids[0], ids[1], ids[2], "input_string")
                ikeystrokes = retrieve_fast(ids[0], ids[1], ids[2], "keystrokes")
                truth = len(ikeystrokes)    

                try:
                    interval, hitcount = analyze_file(path, truth, False)
                except IndexError: 
                    print("Faulty Binary: Recording")
                    errors.append(f"{file}, too small")
                    continue
                except MemoryError:
                    print("Faulty Binary: Memory")
                    errors.append(f"{file}, too big")
                    continue
                formatted = format_json_raw(ids, typed_string, ikeystrokes, interval, hitcount)
                #formatted = format_json(file, interval)
                observations.append(formatted)
                bar.next() 
            export_json(folder, observations)
            export_json(f"{folder}_log", errors)
            
    elif num_arguments == 2:
        if sys.argv[1] == "-h":
            help()
        else:
            folder = f"{BINARY_DIR}/{sys.argv[1]}"
            intervals = []
        
            interval = analyze_file(folder, False)
            formatted = format_json_raw(sys.argv[1], interval)          
            intervals.append(formatted) 
            export_json(sys.argv[1], intervals.tolist())
