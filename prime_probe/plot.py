import matplotlib.pyplot as plt
import numpy as np
import sys


def graph(traces, attack_type, output_file):
    counts = get_hit_count(traces)
    filtered_counts = []

    prev = -100
    for i in range(len(counts)):
        if counts[i] >= 10 and i - prev > 75:
            filtered_counts.append(i)

    print(len(filtered_counts))
    print(filtered_counts)

    plt.figure()
    plt.plot(range(len(counts)), counts, color="red", alpha=0.7, linewidth=1)
    plt.xlabel("time (ms)")
    plt.ylabel("detection count")
    plt.title(attack_type + " Detection Count Line Plot")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.savefig(output_file)
    plt.close()


def get_hit_count(traces):
    timestamps = ((traces - traces[0]) / (3.4 * 1000000)).astype(int)
    sorted_timestamps = np.sort(timestamps)
    total_time_ms = sorted_timestamps[-1] + 1
    counts = np.zeros(total_time_ms, dtype=int)
    for v in sorted_timestamps:
        counts[v] += 1
    return counts


def load_trace(input_file):
    return np.fromfile(input_file, dtype=np.uint64)


if __name__ == "__main__":
    for i in range(8):
        trace = load_trace(f"captured_keystrokes_{str(i)}.bin")
        if len(sys.argv) == 1 or sys.argv[1] == "pp":
            graph(trace, "Prime+Probe", f"pp_outfile{str(i)}.png")
        elif sys.argv[1] == "ps":
            graph(trace, "Prime+Scope", f"ps_outfile{str(i)}.png")
