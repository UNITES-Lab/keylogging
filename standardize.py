import json

keycode_map = {
    # Letters
    30: "a",
    48: "b",
    46: "c",
    32: "d",
    18: "e",
    33: "f",
    34: "g",
    35: "h",
    23: "i",
    36: "j",
    37: "k",
    38: "l",
    50: "m",
    49: "n",
    24: "o",
    25: "p",
    16: "q",
    19: "r",
    31: "s",
    20: "t",
    22: "u",
    47: "v",
    17: "w",
    45: "x",
    21: "y",
    44: "z",
    # Numbers
    2: "1",
    3: "2",
    4: "3",
    5: "4",
    6: "5",
    7: "6",
    8: "7",
    9: "8",
    10: "9",
    11: "0",
    # Whitespace / control
    57: " ",
    28: "\n",
    14: "[BACKSPACE]",
    15: "\t",
    1: "[ESC]",
    # Punctuation
    12: "-",
    13: "=",
    26: "[",
    27: "]",
    43: "\\",
    39: ";",
    40: "'",
    41: "`",
    51: ",",
    52: ".",
    53: "/",
    # Function keys (optional)
    59: "[F1]",
    60: "[F2]",
    61: "[F3]",
    62: "[F4]",
    63: "[F5]",
    64: "[F6]",
    65: "[F7]",
    66: "[F8]",
    67: "[F9]",
    68: "[F10]",
    87: "[F11]",
    88: "[F12]",
}


with open("test.json", "r") as f:
    data = json.load(f)

decoded = "".join(keycode_map.get(k, f"[key{k}]") for k in data["keystrokes"])
data["keystrokes"] = list(decoded)

CPU_FREQ = 3500000000

press_times = data["intervals"]
intervals = []
for i in range(len(press_times)):
    if i > 0:
        interval_ms = round((press_times[i] - press_times[i - 1]) / CPU_FREQ * 1000)
        intervals.append(interval_ms)

data["intervals"] = intervals

with open("standard.json", "w") as f:
    json.dump(data, f, indent=4)
