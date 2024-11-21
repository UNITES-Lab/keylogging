import matplotlib.pyplot as plt
import ast
import numpy as np
from enum import Enum
import json

TIME_MASK = 10000000


def sort_output(data):
    # List to store the extracted numbers
    keypress_output = []
    keyrelease_output = []
    flush_reload_output = []

    start_time = 0

    # Process each line in the log file

    found_start = False
    for line in data:
        if found_start:
            if line.find("ends") != -1:
                break
            elif line.find("{") != -1 and line.find("}") != -1:
                dict_start = line.find("{")
                obj = ast.literal_eval(line[dict_start:])
                if str(obj.get("type")) == "press":
                    keypress_output.append(obj)
                elif str(obj.get("type")) == "release":
                    keyrelease_output.append(obj)
                else:
                    flush_reload_output.append(obj)
            else:
                continue
        else:
            if line.find("starts") != -1:
                found_start = True
                start_time = int(line[line.find(": ") + 2 :])
    return {
        "start_time": start_time,
        "keypresses": keypress_output,
        "keyreleases": keyrelease_output,
        "flush_reload": flush_reload_output,
    }


def graph_keystrokes(data):
    keypresses_output = data["keypresses"]
    keyreleases_output = data["keyreleases"]
    flush_reload_output = data["flush_reload"]

    keystroke_time_kp = [x["keystroke-time"] // TIME_MASK for x in keypresses_output]
    keystroke_time_ff = [x["keystroke-time"] // TIME_MASK for x in flush_reload_output]
    keystroke_time_kr = [x["keystroke-time"] // TIME_MASK for x in keyreleases_output]
    filtered_keystroke_ff = [keystroke_time_ff[0]]
    prev_stroke_time = keystroke_time_ff[0]
    for x in keystroke_time_ff:
        # Fast typers release-press: 121, std: 12
        # Fast typers hold time: 104, std 17
        # Combined: 225, std: 21,
        # 2 std down: 225-42: 183
        if x - prev_stroke_time > 70:
            filtered_keystroke_ff.append(x)
            prev_stroke_time = x

    values_kp = []
    values_kr = []
    values_ff = []
    values_fff = []

    for i in range(0, 2500):
        if i in keystroke_time_kp:
            values_kp.append(1)
        else:
            values_kp.append(0)
    for i in range(0, 2500):
        if i in keystroke_time_kr:
            values_kr.append(1)
        else:
            values_kr.append(0)

    for i in range(0, 2500):
        if i in keystroke_time_ff:
            values_ff.append(1)
        else:
            values_ff.append(0)

    for i in range(0, 2500):
        if i in filtered_keystroke_ff:
            values_fff.append(1)
        else:
            values_fff.append(0)

    time_range = np.arange(0, 2500)

    plt.plot(time_range, values_ff)
    plt.title("Flush+Reload Plot")
    plt.xlabel("Time in 10M cycles")
    plt.ylabel("Hit")
    plt.grid(True)
    plt.savefig("./flush_reload.png")

    plt.clf()

    plt.plot(time_range, values_kp)
    plt.title("Keypresses Plot")
    plt.xlabel("Time in 10M cycles")
    plt.ylabel("Hit")
    plt.grid(True)
    plt.savefig("./keypresses.png")

    plt.clf()

    plt.plot(time_range, values_kr)
    plt.title("Keyreleases plot")
    plt.xlabel("Time in 10M cycles")
    plt.ylabel("Hit")
    plt.grid(True)
    plt.savefig("./keyreleases.png")

    plt.clf()

    plt.plot(time_range, values_fff, "C2", label="flush+reload")
    plt.title("Filtered Flush+Reload Plot")
    plt.xlabel("Time in 10M cycles")
    plt.ylabel("Hit")
    plt.grid(True)
    plt.savefig("./filtered_flush_reload.png")

    plt.plot(time_range, values_kp, "C1", label="keypresses")
    plt.title("Keypresses on Filtered FR Plot")
    plt.savefig("./kpffr.png")

    plt.clf()

    plt.plot(time_range, values_fff, "C2", label="flush+reload")
    plt.xlabel("Time in 10M cycles")
    plt.ylabel("Hit")
    plt.grid(True)
    plt.plot(time_range, values_kr, "C1", label="keyreleases")
    plt.title("Keyreleases on Filtered FR Plot")
    plt.savefig("./krffr.png")

    plt.clf()

    plt.plot(time_range, values_ff, "C2", label="flush+reload")
    plt.xlabel("Time in 10M cycles")
    plt.ylabel("Hit")
    plt.grid(True)
    plt.plot(time_range, values_kr, "C1", label="keyreleases")
    plt.title("Keyreleases on FR Plot")
    plt.savefig("./krfr.png")

    plt.clf()

    plt.plot(time_range, values_ff, "C2", label="flush+reload")
    plt.xlabel("Time in 10M cycles")
    plt.ylabel("Hit")
    plt.grid(True)
    plt.plot(time_range, values_kp, "C1", label="keyreleases")
    plt.title("Keypresses on FR Plot")
    plt.savefig("./kpfr.png")


def write_output(data):
    flush_reload_json = json.dumps(data["flush_reload"], indent=4)
    keypresses_json = json.dumps(data["keypresses"], indent=4)
    keyreleases_json = json.dumps(data["keyreleases"], indent=4)

    with open("flush_reload.json", "w") as outfile:
        outfile.write(flush_reload_json)

    with open("keypresses.json", "w") as outfile:
        outfile.write(keypresses_json)

    with open("keyreleases.json", "w") as outfile:
        outfile.write(keyreleases_json)


if __name__ == "__main__":
    # Path to the log file
    log_file_path = "logs/test.log"
    log_data = ""

    # Open and read the log file
    with open(log_file_path, "r") as log_file:
        log_data = log_file.readlines()

    out = sort_output(log_data)
    write_output(out)
    graph_keystrokes(out)
