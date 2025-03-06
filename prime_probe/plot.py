import numpy as np
from scipy import signal
from dtaidistance import dtw
from dtaidistance import dtw_visualisation
import matplotlib.pyplot as plt
import os
import struct
import ast

def sort_output(data):
    # List to store the extracted numbers
    keypress_output = []
    keyrelease_output = []

    # Process each line in the log file
    start_time = 0;
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

def graph(input_file, attack_type, output_file, normalize):
    values = np.fromfile(input_file, dtype=np.uint64) 
    CPU_FREQ = 3.4
    timestamps = ((values-values[0])/ (3.4 * 1000000)).astype(int)
    sorted_timestamps = np.sort(timestamps)
    print(sorted_timestamps)
    # plotting histogram with 10 ms intervals over 10s
    counts = np.zeros(12000, dtype=int)
    if normalize:
        sorted_timestamps = sorted_timestamps - sorted_timestamps[1]
    for v in sorted_timestamps:
        counts[v] += 1
    strokes = [i for i in counts if i >= 250]
    print("valid detections: " + str(len(strokes)))

    plt.figure()
    plt.plot(range(12000), counts, color='red', alpha=0.7, linewidth=1)
    plt.xlabel("time (ms)")
    plt.ylabel("detection count")
    plt.title(attack_type + " Detection Count Line Plot")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(output_file)

    return values[0]

def stat(input_file, truth_file, normalize):
    values = np.fromfile(input_file, dtype=np.uint64) 
    truth_values = np.fromfile(truth_file, dtype=np.uint64) 
    CPU_FREQ = 3.4
    
    timestamps = ((values-values[0])/ (3.4 * 1000000)).astype(int)
    sorted_timestamps = np.sort(timestamps)

    truths = ((truth_values-truth_values[0])/ (3.4 * 1000000)).astype(int)
    sorted_truths = np.sort(truths)

    counts = np.zeros(12000, dtype=int)
    accurates = []
    grouped = []
    filtered = []

   
    
    for v in sorted_timestamps:
        counts[v] += 1

    filtered = np.where(counts >= 60)[0]         #change this value to adjust threshhold per noise, default is 75 counts
    

    #grouping function
    prev = filtered[0]
    grouped.append(filtered[0])
    for v in filtered:
        if(v-prev > 50):          #change this value to adjust threshhold, default is 10ms
            grouped.append(v)
        prev = v



    #determining normalization factor, find mathcing interval pattern, consider using DTW or measureing the difference in start time in two modules, latter is probably better

    #Kernel module inserted at: 1740674374713510339 ns, Keylogger started at: 1740674374726586827 ns diff = -13076480ns/1000000 = 13.076 ms

    if normalize:
        grouped = np.array(grouped)                           
        grouped = grouped - 2500        #subtract first keystroke time
        sorted_truths = sorted_truths - sorted_truths[1]

    diff_pp = np.diff(grouped)
    diff_truth = np.diff(sorted_truths) 


    #accuracy calculation with +-
    prev = 0
    for k in diff_truth:
        for v in diff_pp[7 + prev:10 + prev]:
            prev += 1
            if (abs(k-v) < 5):            #change this value to adjust threshhold, default is +-5ms
                accurates.append(v)
                break


    

    print(diff_pp[4:])
    print(diff_truth)
    print(accurates)

    # #accuracy calculation with +-
    # for k in diff_truth:
    #     for v in diff_pp:
    #         if (abs(k-v) < 5):            #change this value to adjust threshhold, default is +-5ms
    #             accurates.append(v)
    #             continue
    # print(sorted_truths)
    # print(len(sorted_truths))
    # print(accurates)

    #interval calculation
    
    print("Accuracy: " + str((len(accurates)/len(diff_pp))))
    print("F-value: " + str(np.var(diff_pp[4:])/np.var(diff_truth)))
    # print("Correlation Coefficient: " + str(np.corrcoef(diff_truth, diff_pp[25:])[0, 1]))

    corr = signal.correlate(diff_truth, diff_pp, mode='valid')

    bestMatch = np.argmax(corr)

    print("Best matching starting index:", bestMatch)

    print("DTW Distance: ", dtw.distance(diff_truth, diff_pp[3:]))
    dtw_visualisation.plot_warping(diff_truth, diff_pp[3:], dtw.warping_path(diff_truth, diff_pp[3:]), filename="warp.png")


    
    
    clock = np.arange(64, len(diff_pp), 128)
    fig, (ax_orig, ax_noise, ax_corr) = plt.subplots(3, 1, sharex=True)
    ax_orig.plot(diff_truth, 'b-')
    ax_orig.plot(np.arange(len(diff_truth)), diff_truth, 'ro')
    ax_orig.set_title('Original signal')
    ax_noise.plot(diff_pp)
    ax_noise.set_title('Signal with noise')
    ax_corr.plot(corr, 'b-')
    ax_corr.plot(np.arange(len(diff_truth)), diff_truth, 'ro')
    ax_corr.axhline(0.5, ls=':')
    ax_corr.set_title('Cross-correlated with rectangular pulse')
    ax_orig.margins(0, 0.1)
    fig.tight_layout()
    plt.title(" Cross Correlation Plot")
    plt.savefig("correlation.png")

    # dtw_visualisation.plot_warpingpaths(diff_truth, diff_pp[4:], dtw.warping_paths(diff_truth, diff_pp[4:]), dtw.warping_path(diff_truth, diff_pp[4:]), filename="warp3.png")
    
if __name__ == "__main__":
    graph("pp_keystrokes.bin", "Prime+Probe", "pp_keystrokes.png", False)
    # for i in range(4):
    #     graph("pp_keystrokes_"+str(i) + ".bin", "Prime+Probe", "pp_keystrokes_"+str(i), False);
    output = os.popen("sudo dmesg -c").read().strip().split("\n")
    data = sort_output(output)
    formatted_list = [data["start_time"]] + data["keypresses"] # keystroke time reported from spy is relative to start-time 
    flush_list_to_binary(formatted_list, "kl_keystrokes.bin")
    graph("kl_keystrokes.bin", "Keylogger", "kl_keystrokes.png", True) 
    stat("pp_keystrokes.bin","kl_keystrokes.bin", True)

