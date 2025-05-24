import matplotlib.pyplot as plt
import numpy as np
import sys
import os
import json
from progress.bar import Bar
import heapq
import re

global data
global json_dictionary

CPU_FREQ = 3.4
MIN_KEYSTROKE_INTERVAL = 35
threshold = 15 # TODO: Find a dynamic algorithm to determine the hitcount threshold
BINARY_DIR = "data/binary_data"

def load_json(path):
    
    # convert file into a list of json strings
    with open(path, 'r') as file:
        data = json.load(file)
    
    return data

def extract_ids(filepath):
    """
    Extracts three numbers from a filepath string.
    
    Expected format:
      .../xxx-xxxx-xxxx.bin
    where xxx, xxxx, and xxxx are numeric groups.
    
    Returns:
      A tuple of three integers: (participant, test_section, sentence)
      or None if the pattern doesn't match.
    """
    # Regular expression to match three groups of digits separated by hyphens and ending with .bin
    pattern = r'(\d+)-(\d+)-(\d+)\.bin'
    match = re.search(pattern, filepath)
    if match:
        participant = int(match.group(1))
        test_section = int(match.group(2))
        sentence = int(match.group(3))
        return participant, test_section, sentence
    else:
        return None

def retrieve(json_file, participant_id, test_section_id, sentence_id, query):

    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for record in data:
        if (record.get("participant_id") == participant_id and
            record.get("test_section_id") == test_section_id and
            record.get("sentence_id") == sentence_id):
            return record.get(query)
    return None

def set_threshhold(hits, target):
    threshold = heapq.nlargest((target+10)*5, hits)[-1]
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
    plt.figure()
    plt.plot(range(traces.size), traces, color='red', alpha=0.7, linewidth=1)
    plt.xlabel("time (ms)")
    plt.ylabel("detection count")
    plt.title(attack_type + " Detection Count Line Plot")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(output_file)
    plt.close()

""" This is where the filter function and algorithm resides"""
def get_interval(counts, threshold, speedup):
    potential_keystrokes = {str(i): counts[i] for i in range(len(counts)) if counts[i] > threshold} 

    interval = []
    isFirst = True
    prev = -MIN_KEYSTROKE_INTERVAL # dummy value, assignment change after the first 

    for index in potential_keystrokes:
        index = int(index)
        if isFirst:
            isFirst = False
            prev = index
        elif (index - prev) * speedup > MIN_KEYSTROKE_INTERVAL:
            interval.append((index - prev) * speedup)
            prev = index

    return interval


def load_trace(input_file):
    return np.fromfile(input_file, dtype=np.uint16)

def fix_dips(trace):
   for i in range(len(trace)):
      if trace[i] < 40:
         last = min(i+2000, len(trace)) 
         trace[i:last] += 70
         i+=2000

def analyze_file(path_to_file, truth, fix, speedup):
    pp_trace = load_trace(path_to_file)
    if fix:
        fix_dips(pp_trace)
    print(pp_trace.size)
    keycode_trace = pp_trace[0:pp_trace.size//2]
    event_trace = pp_trace[pp_trace.size//2:]

    threshold = np.sort(keycode_trace)[::-1][3*truth]
    print(threshold)
    return get_interval(keycode_trace.tolist(), threshold, speedup), keycode_trace.tolist()

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
    folder = sys.argv[1] 
    speedup = int(sys.argv[2])
    JSON_PATH = f"data/cleaned_data/{folder}.jsonl"
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
            interval, hitcount = analyze_file(path, truth, True, speedup)
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
    print()
    export_json(folder, observations)
