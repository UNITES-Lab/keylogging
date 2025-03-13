import matplotlib.pyplot as plt
import numpy as np

def graph(input_file, attack_type, output_file, normalize):
    values = np.fromfile(input_file, dtype=np.uint64) 
    CPU_FREQ = 3.4
    timestamps = ((values-values[0])/ (3.4 * 1000000)).astype(int)
    sorted_timestamps = np.sort(timestamps)
    print(sorted_timestamps)
    # plotting histogram with 10 ms intervals over 10s
    counts = np.zeros(20000, dtype=int)
    if normalize:
        sorted_timestamps = sorted_timestamps - sorted_timestamps[1]
    for v in sorted_timestamps:
        counts[v] += 1
    strokes = [i for i in counts if i >= 15]
    print("valid detections: " + str(len(strokes)))

    plt.figure()
    plt.plot(range(20000), counts, color='red', alpha=0.7, linewidth=1)
    plt.xlabel("time (ms)")
    plt.ylabel("detection count")
    plt.title(attack_type + " Detection Count Line Plot")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(output_file)

    return values[0]

if __name__ == "__main__":
            graph("../../output_binary/across_participant_across_sentence_test/337355-3636032-1438.bin", "Prime+Probe", "../../figures/337355-3636032-1438.png", False);
