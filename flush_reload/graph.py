import matplotlib.pyplot as plt
import ast
import numpy as np
from enum import Enum
import json

TIME_MASK = 10000000


def sort_output(data):
    # List to store the extracted numbers
    keylogger_output = []

    flush_reload_output = []

    start_time = 0

    # Process each line in the log file

    found_start = False
    for line in data:
        if found_start:
            if line.find("ends") != -1:
                print(line)
                break
            elif line.find("{") != -1 and line.find("}") != -1:
                dict_start = line.find("{")
                obj = ast.literal_eval(line[dict_start:])
                if obj.get("key-char") is not None:
                    keylogger_output.append(obj)
                else:
                    flush_reload_output.append(obj)
            else:
                print(line)
                continue
        else:
            if line.find("starts") != -1:
                found_start = True
                start_time = int(line[line.find(": ") + 2 :])
                print(line)
    return {
        "start_time": start_time,
        "keylogger": keylogger_output,
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
        if x - prev_stroke_time > 18:
            filtered_keystroke_ff.append(x)
            prev_stroke_time = x

    values_kp = []
    values_kr = []
    values_ff = []
    values_fff = []

    for i in range(0, 1001):
        if i in keystroke_time_kp:
            values_kp.append(1)
        else:
            values_kp.append(0)
    for i in range(0, 1001):
        if i in keystroke_time_kr:
            values_kr.append(1)
        else:
            values_kr.append(0)

    for i in range(0, 1001):
        if i in keystroke_time_ff:
            values_ff.append(1)
        else:
            values_ff.append(0)

    for i in range(0, 1001):
        if i in filtered_keystroke_ff:
            values_fff.append(1)
        else:
            values_fff.append(0)

    time_range = np.arange(0, 1001)

    plt.plot(time_range, values_ff)
    plt.title("Flush+Reload Plot")
    plt.xlabel("Time in 10 ms")
    plt.ylabel("Hit")
    plt.grid(True)
    plt.savefig("./flush_reload.png")

    plt.clf()

    plt.plot(time_range, values_kp)
    plt.title("Keypresses Plot")
    plt.xlabel("Time in 10 ms")
    plt.ylabel("Hit")
    plt.grid(True)
    plt.savefig("./keypresses.png")

    plt.clf()

    plt.plot(time_range, values_kr)
    plt.title("keyreleases plot")
    plt.xlabel("Time in 10 ms")
    plt.ylabel("Hit")
    plt.grid(True)
    plt.savefig("./keyreleases.png")

    plt.clf()

    plt.plot(time_range, values_fff)
    plt.title("Filtered Flush+Reload Plot")
    plt.xlabel("Time in 10 ms")
    plt.ylabel("Hit")
    plt.grid(True)
    plt.savefig("./filtered_flush_reload.png")

    plt.plot(time_range, values_kp)
    plt.title("Keypresses on Filtered FR Plot")
    plt.savefig("./kpfr.png")

    plt.clf()

    plt.plot(time_range, values_fff)
    plt.xlabel("Time in 10 ms")
    plt.ylabel("Hit")
    plt.grid(True)
    plt.plot(time_range, values_kr)
    plt.title("Keyreleases on Filtered FR Plot")
    plt.savefig("./krfr.png")


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
