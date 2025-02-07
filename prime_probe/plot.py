import numpy as np
import matplotlib.pyplot as plt

def graph_bin(filename):
    values = np.fromfile(filename, dtype=np.uint64) - 2030639595640798
    CPU_FREQ = 3.4
    values = (values / (3.4 * 1000000)).astype(int)
    sorted_values = np.sort(values)
    print(sorted_values.shape)
    # plotting histogram with 10 ms intervals over 10s
    slots = np.zeros(10000, dtype=int)
    for v in values:
        slots[v] = 1

    plt.figure()
    plt.bar(range(10000), slots, width=1, color="black")  # Binary visualization
    plt.xlabel("milliseconds")
    plt.ylabel("Presence (1 = detected, 0 = not detected)")
    plt.title("Binary Representation of Keystroke Timings")
    plt.savefig("keystrokes.png")

if __name__ == "__main__":
    graph_bin("keystrokes.bin")
