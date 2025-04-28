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
    doubles = []
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(8)  # 8 bytes for a double
            if not chunk:
                break
            if len(chunk) != 8:
                raise ValueError("File ended unexpectedly in the middle of a double.")
            value = struct.unpack("d", chunk)[0]  # 'd' is format for double
            doubles.append(value)
    return doubles


if __name__ == "__main__":
    baseline_data = read_doubles_from_binary("binary_files/baseline_template.bin")
    keystroke_data = read_doubles_from_binary("binary_files/keystrokes_template.bin")

    difference = []
    for i in range(len(baseline_data)):
        if baseline_data[i] >= 0 and keystroke_data[i] >= 0:
            difference.append(
                {
                    "set": i // ARCHES_NUM_SLICES,
                    "slice": i % ARCHES_NUM_SLICES,
                    "diff": int(
                        (keystroke_data[i] - baseline_data[i]) / baseline_data[i]
                    ),
                }
            )

    difference.sort(key=lambda x: x["diff"], reverse=True)
    print(json.dumps(difference[:64], indent=4))
