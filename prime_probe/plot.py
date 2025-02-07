import numpy as np
import matplotlib.pyplot as plt

def graph_bin(filename):
    values = np.fromfile(filename, dtype=np.uint64) - 2107788755804959
    CPU_FREQ = 3.4
    values = (values / (3.4 * 1000000)).astype(int)
    sorted_values = np.sort(values)
    print(sorted_values.shape)
    # plotting histogram with 10 ms intervals over 10s
    slots = np.zeros(10001, dtype=int)
    counts = np.zeros(10001, dtype=int)
    for v in values:
        counts[v] += 1
        slots[v] = 1

    plt.figure()
    plt.bar(range(10001), slots, width=1, color="black")  # Binary visualization
    plt.xlabel("milliseconds")
    plt.ylabel("Presence (1 = detected, 0 = not detected)")
    plt.title("Binary Representation of Keystroke Timings")
    plt.savefig("keystrokes.png")

    plt.figure()
    plt.plot(range(10001), counts, color='red', alpha=0.7, linewidth=1)
    plt.xlabel("time (ms)")
    plt.ylabel("detection count")
    plt.title("Detection Count Line Plot")
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig("lineplot.png")

if __name__ == "__main__":
    graph_bin("keystrokes.bin")
