import numpy as np
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
    # plotting histogram with 10 ms intervals over 10s
    counts = np.zeros(10001, dtype=int)
    if normalize:
        sorted_timestamps[1:] = sorted_timestamps[1:] - sorted_timestamps[1]
    for v in sorted_timestamps:
        counts[v] += 1
    
    strokes = [i for i in counts if i >= 250]
    print("valid detections: " + str(len(strokes)))

    plt.figure()
    plt.plot(range(10001), counts, color='red', alpha=0.7, linewidth=1)
    plt.xlabel("time (ms)")
    plt.ylabel("detection count")
    plt.title(attack_type + " Detection Count Line Plot")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(output_file)

    return values[0]

    
if __name__ == "__main__":
    pp_start_time = graph("pp_keystrokes.bin", "Prime+Probe", "pp_keystrokes.png", False)
    output = os.popen("sudo dmesg -c").read().strip().split("\n")
    data = sort_output(output)
    formatted_list = [data["start_time"]] + data["keypresses"] # keystroke time reported from spy is relative to start-time 
    # flush_list_to_binary(formatted_list, "kl_keystrokes.bin")
    graph("kl_keystrokes.bin", "Keylogger", "kl_keystrokes.png", True) 

