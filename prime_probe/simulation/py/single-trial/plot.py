import numpy as np
from scipy import signal
from dtaidistance import dtw
from dtaidistance import dtw_visualisation
import matplotlib.pyplot as plt
import os
import struct
import ast
from simulate import load_json
import re
import json

SPEED_UP = 3

def sort_output(data):
    # List to store the extracted numbers
    keypress_output = []
    keyrelease_output = []

    # Process each line in the log file
    start_time = 0
    found_start = False
    for line in data:
        if found_start:
            if line.find("unloaded") != -1:
                break
            elif line.find("{") != -1 and line.find("}") != -1:
                dict_start = line.find("{")
                obj = ast.literal_eval(line[dict_start:])
                if str(obj.get("type")) == "press":
                    keypress_output.append(obj["keystroke-time"])
                elif str(obj.get("type")) == "release":
                    keyrelease_output.append(obj["keystroke-time"])
            else:
                continue
        else:
            if line.find("loaded successfully") != -1:
                found_start = True
                start_time = int(line[line.find(": ") + 2 :])
    return {
        "start_time": start_time, # time reported from spy.c is relative to start time 
        "keypresses": keypress_output,
        "keyreleases": keyrelease_output,
    }

def flush_list_to_binary(data_list, filename):
    """
    Flushes a list of numerical data to a binary file.

    Args:
        data_list: The list of data to be written.
        filename: The name of the file to write to.
    """
    with open(filename, 'wb') as file:
        for item in data_list:
            # Assuming data is float, use 'f'. Adjust format if needed ('i' for int, etc.)
            binary_data = struct.pack('<Q', item)
            file.write(binary_data)
        file.flush()
        os.fsync(file.fileno())

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

def find_threshhold(counts, target):
    low = 0
    high = int(counts.max())
    best_v = low
    best_diff = float('inf')
    
    while low <= high:
        mid = 20
        filtered = np.where(counts >= mid)[0]
        num_filtered = len(filtered)
        diff = abs(num_filtered - target)
        
        if diff == 0:
            return mid
        
        if diff < best_diff:
            best_diff = diff
            best_v = mid
        
        if num_filtered > target:
            low = mid + 3
        else:
            high = mid - 3
            
    return best_v

def graph(input_file, truth_file, attack_type, output_file, normalize):

    values = np.fromfile(input_file, dtype=np.uint64) 
    CPU_FREQ = 3.4
    timestamps = ((values-values[0])*SPEED_UP/ (3.4 * 1000000)).astype(int)
    sorted_timestamps = np.sort(timestamps)
    print(sorted_timestamps)
    # plotting histogram with 10 ms intervals over 10s
    sorted_timestamps = sorted_timestamps - sorted_timestamps[1]
    timerange = sorted_timestamps[-1] - sorted_timestamps[0]+1
    counts = np.zeros(timerange, dtype=int)        
    for v in sorted_timestamps:
        counts[v] += 1
    strokes = [i for i in counts if i >= 20]
    print("valid detections: " + str(len(strokes)))
    

    ids = extract_ids(input_file)
    intervals = retrieve(truth_file,ids[0], ids[1], ids[2], "intervals")
    intervals[0] = 0
    truths = np.cumsum(intervals)
    truths += 1200
    print("ground truth: " + str(len(truths)))


    plt.figure()
    plt.plot(range(len(counts)), counts, color='red', alpha=0.7, linewidth=1)
    for t in truths:
        plt.axvline(x=t, color='blue', linestyle=':', alpha=0.7)
    plt.xlabel("time (ms)")
    plt.ylabel("detection count")
    plt.title(attack_type + " Detection Count Line Plot")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(output_file)

    return values[0]

def stat(input_file, truth_file, normalize):
    values = np.fromfile(input_file, dtype=np.uint64) 
    CPU_FREQ = 3.4
    
    timestamps = ((values-values[0])*SPEED_UP/ (3.4 * 1000000)).astype(int)
    sorted_timestamps = np.sort(timestamps)
    sorted_timestamps = sorted_timestamps - sorted_timestamps[1]
    timerange = sorted_timestamps[-1] - sorted_timestamps[0]+1

    ids = extract_ids(input_file)
    intervals = retrieve(truth_file,ids[0], ids[1], ids[2], "intervals")
    intervals[0] = 0
    truths = np.cumsum(intervals)
    truths += 1000
    
    # truths += 800

    counts = np.zeros(timerange, dtype=int)
    grouped = []
    filtered = []

    
    for v in sorted_timestamps:
        counts[v] += 1
    # count_threshhold = find_threshhold(counts, len(intervals))
    # print("count threshold: ", count_threshhold)
    filtered = np.where(counts >= 20)[0]         #change this value to adjust threshhold per noise, default is 20 counts
    

    #grouping function
    # threshhold = np.mean(intervals) - (2.5*np.std(intervals))
    # print(np.mean(intervals), np.std(intervals))
    # print("grouping threshold: ", threshhold)
    prev = filtered[0]
    grouped.append(0)
    for v in filtered:
        if(v-prev > 35):          #change this value to adjust threshhold, default is 85ms 121 - 3SD(12) = 85ms
            v += 15
            grouped.append(v)
        prev = v



    #determining normalization factor, find mathcing interval pattern, consider using DTW or measureing the difference in start time in two modules, latter is probably better

    if normalize:
        grouped = np.array(grouped)                           
        grouped = grouped - 2500        #subtract first keystroke time

    diff_pp = np.diff(grouped)

    diff_pp[0] = 0

    print(diff_pp)
    print(intervals)

    # #accuracy calculation with +-
    # for k in intervals:
    #     for v in diff_pp:
    #         if (abs(k-v) < 5):            #change this value to adjust threshhold, default is +-5ms
    #             accurates.append(v)
    #             continue
    # print(sorted_truths)
    # print(len(sorted_truths))
    # print(accurates)

    #interval calculation
    print("avg hitcount: " + str(np.sum(counts)/(2*len(filtered))))
    print("valid detections: " + str(len(diff_pp)))
    print("ground truth: " + str(len(intervals)))
    print("F-value: " + str(np.var(diff_pp[4:])/np.var(intervals)))
    # print("Correlation Coefficient: " + str(np.corrcoef(intervals, diff_pp[25:])[0, 1]))

    corr = signal.correlate(diff_pp, intervals, mode='same') / len(intervals)

    bestMatch = np.argmax(corr)

    print("Best matching starting index:", bestMatch)

    print("DTW Distance: ", dtw.distance(intervals, diff_pp))
    dtw_visualisation.plot_warping(intervals, diff_pp, dtw.warping_path(intervals, diff_pp), filename="warp.png")

    
    
    ##Fix Cross Correlation

    fig, (ax_orig, ax_noise, ax_corr) = plt.subplots(3, 1, sharex=True)

    ax_orig.plot(intervals, 'b-')
    ax_orig.plot(np.arange(len(intervals)), intervals, 'ro')
    ax_orig.set_title('Original signal')

    ax_noise.plot(diff_pp)
    ax_noise.set_title('Signal with noise')

    ax_corr.plot(np.arange(len(intervals)), intervals, 'ro')
    ax_corr.axhline(500, ls=':')
    ax_corr.set_title('Cross-correlated with rectangular pulse')

    ax_orig.margins(0, 0.1)
    fig.tight_layout()

    plt.title(" Cross Correlation Plot")
    plt.savefig("correlation.png")

    # dtw_visualisation.plot_warpingpaths(intervals, diff_pp[4:], dtw.warping_paths(intervals, diff_pp[4:]), dtw.warping_path(intervals, diff_pp[4:]), filename="warp3.png")
    
if __name__ == "__main__":
    dir = "split_13"
    filename = "397441-4290094-1372.bin"
    graph(f"bins_to_convert/{dir}/{filename}", f"data/split_json_files/{dir}.jsonl", "Prime+Probe", "pp_keystrokes.png", True)
    stat(f"bins_to_convert/{dir}/{filename}", f"data/split_json_files/{dir}.jsonl", True)
    print(f"{dir}/{filename}")
