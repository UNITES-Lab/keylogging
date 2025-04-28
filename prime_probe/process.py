import numpy as np
import struct
import json

ARCHES_NUM_SLICES = 4


def load_json(path):

    # convert file into a list of json strings
    with open(path, "r") as file:
        data = json.load(file)

    return data


def read_doubles_from_binary(filename):
    return np.fromfile(filename, dtype=np.float64)


def report_statistics(arr):
    to_delete = []
    for i in range(arr.size):
        if arr[i] < 0:
            to_delete.append(i)

    temp_arr = np.delete(arr, to_delete)
    stats = {
        "count": temp_arr.size,
        "mean": np.mean(temp_arr),
        "std_dev": np.std(temp_arr, ddof=1),  # sample standard deviation
        "min": np.min(temp_arr),
        "25%": np.percentile(temp_arr, 25),
        "median": np.median(temp_arr),
        "75%": np.percentile(temp_arr, 75),
        "max": np.max(temp_arr),
    }

    print("------------------------------------------")
    for key, value in stats.items():
        print(f"{key:>6}: {value:.4f}")


if __name__ == "__main__":
    baseline_data = read_doubles_from_binary("binary_files/baseline_template.bin")
    keystroke_data = read_doubles_from_binary("binary_files/keystrokes_template.bin")
    report_statistics(baseline_data)
    report_statistics(keystroke_data)

    activity_data = []
    for i in range(len(baseline_data)):
        if baseline_data[i] >= 0 and keystroke_data[i] >= 0:
            activity_data.append(
                {
                    "set": i // ARCHES_NUM_SLICES,
                    "slice": i % ARCHES_NUM_SLICES,
                    "diff": int(
                        (keystroke_data[i] - baseline_data[i]) / baseline_data[i]
                    ),
                }
            )

    activity_data = [x for x in activity_data if x["diff"] > 0]
    activity_data.sort(key=lambda x: x["diff"], reverse=True)

    difference = [x["diff"] for x in activity_data]
    report_statistics(np.array(difference))
    print(json.dumps(activity_data[:64], indent=4))
