import json
import numpy as np
import sys
import matplotlib.pyplot as plt

def graph(traces, attack_type, output_file):
    plt.figure()
    plt.plot(range(len(traces)), traces, color='red', alpha=0.7, linewidth=1)
    plt.xlabel("time (ms)")
    plt.ylabel("detection count")
    plt.title(attack_type + " Detection Count Line Plot")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(output_file)
    plt.close()

def load_json(path):

    # convert file into a list of json strings
    with open(path, "r") as file:
        data = json.load(file)

    return data

def load_trace(input_file):
    return np.fromfile(input_file, dtype=np.uint64)

def get_hit_count(traces):
    timestamps = ((traces-traces[0])/ (3.4 * 1000000)).astype(int)
    sorted_timestamps = np.sort(timestamps)
    total_time_ms = sorted_timestamps[-1]+1
    counts = np.zeros(total_time_ms, dtype=int)
    for v in sorted_timestamps:
        counts[v] += 1
    return counts

def duplicate_list(in_list, speedup):
    return [e for e in in_list for _ in range(int(speedup))] 

def analyze_file(path_to_file, truth, file, sentence_id, speedup):
    pp_trace = load_trace(path_to_file)
    counts_per_ms = duplicate_list(get_hit_count(pp_trace), speedup)
    graph(counts_per_ms, "Keycode Browser PP", f"figures/{file}_{sentence_id}_keycode.png");

if __name__ == "__main__":
   data = load_json(f"data/cleaned_data/{sys.argv[1]}.jsonl")
   for sentence in data: 
      sentence_id = f"{sentence["participant_id"]}-{sentence["test_section_id"]}-{sentence["sentence_id"]}"  
      if(sentence_id == sys.argv[2]):
         analyze_file(f"data/binary_data/{sys.argv[1]}/{sentence_id}.bin", 0, sys.argv[1], sys.argv[2], sys.argv[3])
