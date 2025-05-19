import uinput 
import time
import json
import os
import sys
from keymap import *
import requests

# import shared memory
from multiprocessing import shared_memory, Manager

BASE_URL = "http://localhost:8080"


def load_json(path):

    # convert file into a list of json strings
    with open(path, "r") as file:
        data = json.load(file)

    return data


def simulate(device, data, speedup):

    keystrokes = data["keystrokes"]
    intervals = data["intervals"]

    # check if keystrokes and intervals match in the dataset
    assert len(keystrokes) == len(intervals) + 1

    # emit first click
    if keystrokes[0] in KEY_MAP:
        device.emit_click(KEY_MAP[keystrokes[0]])
    else:
        device.emit_click(KEY_MAP[" "])

    for i in range(0, len(intervals)):
        # wait for interval using time.sleep
        wait_interval_ms = intervals[i] / (1000 * speedup)
        time.sleep(wait_interval_ms)

        # emit the next keystroke
        key = keystrokes[i + 1]

        if key in KEY_MAP:
            device.emit_click(KEY_MAP[key])
        else:
            device.emit_click(KEY_MAP[" "])


def scan_keystrokes(data):
    all_keystrokes = []
    not_found_keys = []
    for sentence in data:
        all_keystrokes.extend(sentence["keystrokes"])
    all_keystrokes = set(all_keystrokes)
    for keystroke in all_keystrokes:
        found = False
        for key in KEY_MAP:
            if keystroke == key:
                found = True
                break
        if not found:
            not_found_keys.append(keystroke)
    return not_found_keys


def get_total_duration(data, speedup):
    duration_ms = 0
    for sentence in data:
        duration_ms += sum(sentence["intervals"])
    duration_ms /= speedup
    duration_s = duration_ms // 1000
    duration_ms -= duration_s * 1000
    duration_min = duration_s // 60
    duration_s -= duration_min * 60
    duration_hr = duration_min // 60
    duration_min -= duration_hr * 60
    duration_day = duration_hr // 24
    duration_hr -= duration_day * 24
    return [duration_day, duration_hr, duration_min, duration_s, duration_ms]


def debugPrint(data):
    durations = [sum(obj["intervals"]) for obj in data]
    print(durations)
    print(max(durations))


def js_to_python_bool(b):
    if b == "true":
        return True
    elif b == "false":
        return False
    else:
        return b


def wait_for(signal: str, desired_result: bool):
    sig = not desired_result
    while sig != desired_result:
        response = requests.get(f"{BASE_URL}/get_{signal}")
        sig = js_to_python_bool(response.json()["status"])
        time.sleep(0.01)


def setsig(signal: str, obj=None):
    status = 100
    while status != 200:
        if obj == None:
            response = requests.post(f"{BASE_URL}/set_{signal}")
        else:
            response = requests.post(f"{BASE_URL}/set_{signal}", json=obj)
        status = response.status_code


if __name__ == "__main__":
    # Speedup for the experiments
    SPEEDUP = 3

    # register the uinput device
    device = uinput.Device(KEY_MAP.values())

    data = load_json("within_participant_across_sentence_test.jsonl")

    print(len(data))
    duration = get_total_duration(data, SPEEDUP)
    print(duration)
    count = 0;
    for sentence in data:
        sentence_id = f"{sentence["participant_id"]}-{sentence["test_section_id"]}-{sentence["sentence_id"]}"
        print()
        print(f"{count}: {sentence_id}\t {sentence["input_string"]}")
        wait_for("status", True) 
        setsig("sentence_id", {"sentence_id": sentence_id})
        setsig("start")
        wait_for("ack", True)
        simulate(device, sentence, SPEEDUP)
        setsig("end")
        count += 1

    wait_for("status", True)
    setsig("done")
