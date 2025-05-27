import matplotlib.pyplot as plt
import numpy as np
import sys
from simulate import load_json

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

def duplicate_list(in_list, speedup):
    return [e for e in in_list for _ in range(int(speedup))] 

def analyze_file(path_to_file, truth, file, sentence_id, fix, speedup):
   pp_trace = load_trace(path_to_file)
   if fix:
      fix_dips(pp_trace)
   keycode_trace = np.array(duplicate_list(pp_trace[0:pp_trace.size//2], speedup))
   event_trace = pp_trace[pp_trace.size//2:]
   graph(keycode_trace, "Keycode Browser PP", f"figures/{file}_{sentence_id}_keycode.png");
   graph(event_trace, "Event Browser PP", f"figures/{file}_{sentence_id}_event.png");


if __name__ == "__main__":
   data = load_json(f"data/cleaned_data/{sys.argv[1]}.jsonl")
   for sentence in data: 
      sentence_id = f"{sentence["participant_id"]}-{sentence["test_section_id"]}-{sentence["sentence_id"]}"  
      if(sentence_id == sys.argv[2]):
         analyze_file(f"data/binary_data/{sys.argv[1]}/{sentence_id}.bin", 0, sys.argv[1], sys.argv[2], True, sys.argv[3])
