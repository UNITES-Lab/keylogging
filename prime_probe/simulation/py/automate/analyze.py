import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def graph(input_file, attack_type, output_file, normalize):
    values = np.fromfile(input_file, dtype=np.uint64) 
    CPU_FREQ = 3.4
    timestamps = ((values-values[0])/ (3.4 * 1000000)).astype(int)
    sorted_timestamps = np.sort(timestamps)
    # plotting histogram with 10 ms intervals over 10s
    graph_dimensions = sorted_timestamps[-1]+1
    counts = np.zeros(graph_dimensions, dtype=int)
    if normalize:
        sorted_timestamps = sorted_timestamps - sorted_timestamps[1]
    for v in sorted_timestamps:
        counts[v] += 1
    strokes = [i for i in counts if i >= 15]
    print("valid detections: " + str(len(strokes)))

    plt.figure()
    plt.plot(range(graph_dimensions), counts, color='red', alpha=0.7, linewidth=1)
    plt.xlabel("time (ms)")
    plt.ylabel("detection count")
    plt.title(attack_type + " Detection Count Line Plot")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(output_file)
    plt.close()

    return values[0]

if __name__ == "__main__":
    if len(sys.argv) == 1:
        directories = os.listdir("simulation/output_binary")
        for directory in directories:
            files = os.listdir(f"simulation/output_binary/{directory}")
            for file in files:
                graph(f"simulation/output_binary/{directory}/{file}", f"{file[:-4]} PP Trace", f"simulation/figures/{directory}/{file[:-4]}.png", False)
    elif len(sys.argv) == 2:
        files = os.listdir(f"simulation/output_binary/{sys.argv[1]}")
        for file in files:
            graph(f"simulation/output_binary/{sys.argv[1]}/{file}", f"{file[:-4]} PP Trace", f"simulation/figures/{sys.argv[1]}/{file[:-4]}.png", False)

