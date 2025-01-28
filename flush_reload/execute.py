import time
import json
import os
from pynput.keyboard import Controller
import signal  # handle sigsegv
import argparse
import multiprocessing as mp
import graph
import sys
stop_event = mp.Event()

import uinput

KEY_MAP = {
    # Letters (lowercase)
    "a": uinput.KEY_A,
    "b": uinput.KEY_B,
    "c": uinput.KEY_C,
    "d": uinput.KEY_D,
    "e": uinput.KEY_E,
    "f": uinput.KEY_F,
    "g": uinput.KEY_G,
    "h": uinput.KEY_H,
    "i": uinput.KEY_I,
    "j": uinput.KEY_J,
    "k": uinput.KEY_K,
    "l": uinput.KEY_L,
    "m": uinput.KEY_M,
    "n": uinput.KEY_N,
    "o": uinput.KEY_O,
    "p": uinput.KEY_P,
    "q": uinput.KEY_Q,
    "r": uinput.KEY_R,
    "s": uinput.KEY_S,
    "t": uinput.KEY_T,
    "u": uinput.KEY_U,
    "v": uinput.KEY_V,
    "w": uinput.KEY_W,
    "x": uinput.KEY_X,
    "y": uinput.KEY_Y,
    "z": uinput.KEY_Z,

    # Digits (top row)
    "1": uinput.KEY_1,
    "2": uinput.KEY_2,
    "3": uinput.KEY_3,
    "4": uinput.KEY_4,
    "5": uinput.KEY_5,
    "6": uinput.KEY_6,
    "7": uinput.KEY_7,
    "8": uinput.KEY_8,
    "9": uinput.KEY_9,
    "0": uinput.KEY_0,

    # Common punctuation on QWERTY
    "`": uinput.KEY_GRAVE,       # Backtick / Grave accent
    "-": uinput.KEY_MINUS,
    "=": uinput.KEY_EQUAL,
    "[": uinput.KEY_LEFTBRACE,
    "]": uinput.KEY_RIGHTBRACE,
    "\\": uinput.KEY_BACKSLASH,
    ";": uinput.KEY_SEMICOLON,
    "'": uinput.KEY_APOSTROPHE,
    ",": uinput.KEY_COMMA,
    ".": uinput.KEY_DOT,
    "/": uinput.KEY_SLASH,

    # Whitespace/Control keys
    "Space": uinput.KEY_SPACE,
    "Tab": uinput.KEY_TAB,
    "Enter": uinput.KEY_ENTER,
    "Backspace": uinput.KEY_BACKSPACE,

    # Modifier keys
    "LeftShift": uinput.KEY_LEFTSHIFT,
    "RightShift": uinput.KEY_RIGHTSHIFT,
    "LeftCtrl": uinput.KEY_LEFTCTRL,
    "RightCtrl": uinput.KEY_RIGHTCTRL,
    "LeftAlt": uinput.KEY_LEFTALT,
    "RightAlt": uinput.KEY_RIGHTALT,
    "CapsLock": uinput.KEY_CAPSLOCK,

    # Navigation keys
    "Esc": uinput.KEY_ESC,
    "Up": uinput.KEY_UP,
    "Down": uinput.KEY_DOWN,
    "Left": uinput.KEY_LEFT,
    "Right": uinput.KEY_RIGHT,
    "Home": uinput.KEY_HOME,
    "End": uinput.KEY_END,
    "PageUp": uinput.KEY_PAGEUP,
    "PageDown": uinput.KEY_PAGEDOWN,
    "Insert": uinput.KEY_INSERT,
    "Delete": uinput.KEY_DELETE,

    # Function keys
    "F1": uinput.KEY_F1,
    "F2": uinput.KEY_F2,
    "F3": uinput.KEY_F3,
    "F4": uinput.KEY_F4,
    "F5": uinput.KEY_F5,
    "F6": uinput.KEY_F6,
    "F7": uinput.KEY_F7,
    "F8": uinput.KEY_F8,
    "F9": uinput.KEY_F9,
    "F10": uinput.KEY_F10,
    "F11": uinput.KEY_F11,
    "F12": uinput.KEY_F12
}

def get_address(func: str) -> str:
    output = os.popen(f"sudo cat /proc/kallsyms | grep {func}").read().strip()
    return output


def handle_signal(signum, frame):
    exit(0)


def install_mod():
    print("make clean")
    os.system("make clean")
    print("make")
    os.system("make")
    print("sudo insmod spy.ko")
    print("Please start typing into any window: ")
    os.system("sudo insmod spy.ko")


# def start_keystrokes():
#     keyboard = Controller()

#     print("gvim")
#     os.system("gvim")

#     print('xdotool search --name "gvim"')
#     window_id = os.popen('xdotool search --name "gvim"')
#     print(f"xdotool windowactivate {window_id}")
#     os.system(f"xdotool windowactivate {window_id}")

#     start_time = time.time_ns()
#     print(f"keystroke starts: {start_time}")


def test():
    device = uinput.Device(KEY_MAP.values())
    time.sleep(0.3)
    while not stop_event.is_set():
        # device.emit_click(uinput.KEY_A)
        # time.sleep(0.01)
        # device.emit_click(uinput.KEY_S)
        # time.sleep(0.005)
        # device.emit_click(uinput.KEY_D)
        # time.sleep(0.0124)
        #device.emit_click(uinput.KEY_F)
        #time.sleep(0.0200)
        #device.emit_click(uinput.KEY_F)
        #time.sleep(0.0300)
        device.emit_click(uinput.KEY_F)
        #TODO: use time.time_ns to sync time, how to simulate keyhold time???
        data = data["keypresses"] = [   
            {
                "key-char": "f",
                "keystroke-time": time.time_ns - data["start_time"],
            }
            for key in keypresses
            if key["time"] > data["start_time"]
        ]

        time.sleep(.015)

def simulate(keystrokes):
    device = uinput.Device(KEY_MAP.values())

    with open(keystrokes, "r") as f:
        fLines = f.readlines()
        for line1, line2 in zip(fLines, fLines[1:0]):

            line1 = line1.strip()
            line2 = line2.strip()

            parts1 = line1.split()
            parts2 = line2.split()

            if len(parts1) < 2:
                print(f"Skipping malformed line: {line}")
                continue

            #pull values, TODO: needs modification
            pressedChar, pressTime, nextPressTime = parts1[4], parts1[5], parts2[5]

            try:
                interval = float(pressTime - nextPressTime)
            except ValueError:
                print(f"Invalid wait time '{wait_time_str}' in line: {line}")
                continue


            #simulate keystroke, TODO: may need additional formatting
            device.emit_click(KEY_MAP[char])

            #wait to simulate timing, TODO: determine if sleep() gives good enough granularity, replace with time_ns()
            time.sleep(interval/100)



    # Modify this code to simulate the keystroke patterns you want to automate
    # while not stop_event.is_set():
    #     keyboard.press("a")
    #     keypresses.append({"key-char": "a", "time": time.time_ns()})
    #     time.sleep(0.05)  # hold key for 100 ms
    #     keyboard.release("a")
    #     keyreleases.append({"key-char": "a", "time": time.time_ns()})
    #     time.sleep(0.2)  # wait for 200 ms before next press


def uninstall_mod():
    print("sudo rmmod spy")
    os.system("sudo rmmod spy")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--real", action="store_true", default=False, help="real keystroke mode"
    )
    args = parser.parse_args()
    if not args.real:
        with mp.Manager() as manager:
            keypresses = manager.list()
            keyreleases = manager.list()
            p = mp.Process(target=install_mod)
            q = mp.Process(target=test)
            p.start()
            q.start()
            p.join()
            stop_event.set()
            q.join()
    
            uninstall_mod()
    
            # Capture dmesg output
            output = os.popen("sudo dmesg -c").read().strip().split("\n")
            data = graph.sort_output(output)
    
            """
            Because simulated keys from pynput does not trigger keylogger, we will need to log the inputs by ourselves
            """
    
            data["keypresses"] = [
                {
                    "key-char": key["key-char"],
                    "keystroke-time": key["time"] - data["start_time"],
                }
                for key in keypresses
                if key["time"] > data["start_time"]
            ]
    
            data["keyreleases"] = [
                {
                    "key-char": key["key-char"],
                    "keystroke-time": key["time"] - data["start_time"],
                }
                for key in keyreleases
                if key["time"] > data["start_time"]
            ]
    
            graph.write_output(data)
            graph.graph_keystrokes(data)
    else:
        install_mod()
        time.sleep(1)
        test()
        time.sleep(1)
        uninstall_mod()
        output = os.popen("sudo dmesg -c").read().strip().split("\n")
        data = graph.sort_output(output)
        graph.write_output(data)
        graph.graph_keystrokes(data)
