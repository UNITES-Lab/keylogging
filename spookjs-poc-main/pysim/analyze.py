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
    plt.figure()
    plt.plot(range(traces.size), traces, color='red', alpha=0.7, linewidth=1)
    plt.xlabel("time (ms)")
    plt.ylabel("detection count")
    plt.title(attack_type + " Detection Count Line Plot")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(output_file)
    plt.close()

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
    return np.fromfile(input_file, dtype=np.uint16)

def fix_dips(trace):
   for i in range(len(trace)):
      if trace[i] < 40:
         last = min(i+2000, len(trace)) 
         trace[i:last] += 70
         i+=2000

def analyze_file(path_to_file, truth, fix):
   pp_trace = load_trace(path_to_file)
   if fix:
      fix_dips(pp_trace)
   print(pp_trace.size)
   keycode_trace = pp_trace[0:pp_trace.size//2]
   event_trace = pp_trace[pp_trace.size//2:]

   graph(keycode_trace, "Keycode Browser PP", f"keycode_{fix}.png");
   graph(event_trace, "Event Browser PP", f"event_{fix}.png");
   threshold = np.sort(keycode_trace)[::-1][3*truth]
   print(threshold)
   print(get_interval(keycode_trace.tolist(), threshold))
   print(get_interval(event_trace.tolist(), 500))

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
   data = load_json(f"../cleaned_data/{sys.argv[1]}.jsonl")
   for sentence in data: 
      sentence_id = f"{sentence["participant_id"]}-{sentence["test_section_id"]}-{sentence["sentence_id"]}"  
      if(sentence_id == sys.argv[2]):
         truth = len(sentence["keystrokes"])
         print("actual: " + truth)
         print("observed: " + sentence["intervals"])
         analyze_file(f"data/output_data/{sys.argv[1]}/{sentence_id}.bin", truth, True)
