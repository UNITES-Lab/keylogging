import time
import json
import os
import signal  # handle sigsegv
import argparse
import multiprocessing as mp
import graph
import sys
import uinput

stop_event = mp.Event()



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
    " ": uinput.KEY_SPACE,
    "Tab": uinput.KEY_TAB,
    "Enter": uinput.KEY_ENTER,
    "BKSP": uinput.KEY_BACKSPACE,

    # Modifier keys
    "SHIFT": uinput.KEY_LEFTSHIFT,
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
    "F12": uinput.KEY_F12,

        # Uppercase letters
    "A": uinput.KEY_A,
    "B": uinput.KEY_B,
    "C": uinput.KEY_C,
    "D": uinput.KEY_D,
    "E": uinput.KEY_E,
    "F": uinput.KEY_F,
    "G": uinput.KEY_G,
    "H": uinput.KEY_H,
    "I": uinput.KEY_I,
    "J": uinput.KEY_J,
    "K": uinput.KEY_K,
    "L": uinput.KEY_L,
    "M": uinput.KEY_M,
    "N": uinput.KEY_N,
    "O": uinput.KEY_O,
    "P": uinput.KEY_P,
    "Q": uinput.KEY_Q,
    "R": uinput.KEY_R,
    "S": uinput.KEY_S,
    "T": uinput.KEY_T,
    "U": uinput.KEY_U,
    "V": uinput.KEY_V,
    "W": uinput.KEY_W,
    "X": uinput.KEY_X,
    "Y": uinput.KEY_Y,
    "Z": uinput.KEY_Z,

    # Shift-modified symbols
    "!": uinput.KEY_1,
    "@": uinput.KEY_2,
    "#": uinput.KEY_3,
    "$": uinput.KEY_4,
    "%": uinput.KEY_5,
    "^": uinput.KEY_6,
    "&": uinput.KEY_7,
    "*": uinput.KEY_8,
    "(": uinput.KEY_9,
    ")": uinput.KEY_0,
    "~": uinput.KEY_GRAVE,
    "_": uinput.KEY_MINUS,
    "+": uinput.KEY_EQUAL,
    "{": uinput.KEY_LEFTBRACE,
    "}": uinput.KEY_RIGHTBRACE,
    "|": uinput.KEY_BACKSLASH,
    ":": uinput.KEY_SEMICOLON,
    "\"": uinput.KEY_APOSTROPHE,
    "<": uinput.KEY_COMMA,
    ">": uinput.KEY_DOT,
    "?": uinput.KEY_SLASH
}

SHIFT_MAP = {
    # Uppercase letters
    "A": uinput.KEY_A,
    "B": uinput.KEY_B,
    "C": uinput.KEY_C,
    "D": uinput.KEY_D,
    "E": uinput.KEY_E,
    "F": uinput.KEY_F,
    "G": uinput.KEY_G,
    "H": uinput.KEY_H,
    "I": uinput.KEY_I,
    "J": uinput.KEY_J,
    "K": uinput.KEY_K,
    "L": uinput.KEY_L,
    "M": uinput.KEY_M,
    "N": uinput.KEY_N,
    "O": uinput.KEY_O,
    "P": uinput.KEY_P,
    "Q": uinput.KEY_Q,
    "R": uinput.KEY_R,
    "S": uinput.KEY_S,
    "T": uinput.KEY_T,
    "U": uinput.KEY_U,
    "V": uinput.KEY_V,
    "W": uinput.KEY_W,
    "X": uinput.KEY_X,
    "Y": uinput.KEY_Y,
    "Z": uinput.KEY_Z,

    # Shift-modified symbols
    "!": uinput.KEY_1,
    "@": uinput.KEY_2,
    "#": uinput.KEY_3,
    "$": uinput.KEY_4,
    "%": uinput.KEY_5,
    "^": uinput.KEY_6,
    "&": uinput.KEY_7,
    "*": uinput.KEY_8,
    "(": uinput.KEY_9,
    ")": uinput.KEY_0,
    "~": uinput.KEY_GRAVE,
    "_": uinput.KEY_MINUS,
    "+": uinput.KEY_EQUAL,
    "{": uinput.KEY_LEFTBRACE,
    "}": uinput.KEY_RIGHTBRACE,
    "|": uinput.KEY_BACKSLASH,
    ":": uinput.KEY_SEMICOLON,
    "\"": uinput.KEY_APOSTROPHE,
    "<": uinput.KEY_COMMA,
    ">": uinput.KEY_DOT,
    "?": uinput.KEY_SLASH
}


def get_address(func: str) -> str:
    output = os.popen(f"sudo cat /proc/kallsyms | grep {func}").read().strip()
    return output


def handle_signal(signum, frame):
    exit(0)


def install_mod():
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
    char = "a"
    time.sleep(0.3)
    timing = [   
            {
                "start-time": time.time_ns()
            }
        ]
    

    while not stop_event.is_set():
        device.emit_click(KEY_MAP[char],1)
        #TODO: use time.time_ns to sync time, how to simulate keyhold time???
        timing = [   
            {
                "key-char": KEY_MAP[char],
                "keystroke-time": time.time_ns()
            }
        ]
        time.sleep(.15)
        device.emit_click(KEY_MAP[char],0)
        timing = [   
            {
                "key-char": KEY_MAP[char],
                "keystroke-time": time.time_ns()
            }
        ]
        time.sleep(.5)
    
        # device.emit_click(KEY_MAP[char],1)
        # #TODO: use time.time_ns to sync time, how to simulate keyhold time???
        # timing = [   
        #     {
        #         "key-char": KEY_MAP[char],
        #         "keystroke-time": time.time_ns()
        #     }
        # ]
        # time.sleep(.3)
        # device.emit_click(KEY_MAP[char],0)
        # #TODO: use time.time_ns to sync time, how to simulate keyhold time???
        # timing = [   
        #     {
        #         "key-char": KEY_MAP[char],
        #         "keystroke-time": time.time_ns()
        #     }
        # ]

def simulate():         #TODO: account for gaps between sentences
    device = uinput.Device(KEY_MAP.values())
    time.sleep(0.3)
    with open("5_keystrokes.txt", 'r', encoding='utf-8') as f:
        fLines = [line.strip() for line in f if line.strip()]
        
        shiftPressTime = 0
        shiftReleaseTime = 0

        for line1, line2 in zip(fLines[1:], fLines[2:]):
            parts1 = line1.strip().split("\t")
            parts2 = line2.strip().split("\t")

            #pull values
            pressedChar = parts1[-2]
            pressTime, nextPressTime = float(parts1[-4]), float(parts2[-4])
            releaseTime = float(parts1[-3])
            interval = float(nextPressTime - pressTime)

            if pressedChar == "SHIFT":
                shiftPressTime = pressTime
                shiftReleaseTime = releaseTime
                continue

            elif pressedChar in SHIFT_MAP:
                device.emit_click(KEY_MAP["SHIFT"],1)
                time.sleep((pressTime - shiftPressTime) / 1000)
                timing.append({
                    "key-char": "SHIFT",
                    "keystroke-time": time.time_ns()
                })

                device.emit_click(KEY_MAP[pressedChar],1)
                if shiftReleaseTime > releaseTime:
                    device.emit_click(KEY_MAP[pressedChar],0)
                    time.sleep((shiftReleaseTime - releaseTime) / 1000)
                    device.emit_click(KEY_MAP["SHIFT"],0)
                else:
                    device.emit_click(KEY_MAP["SHIFT"],0)
                    time.sleep((releaseTime - shiftReleaseTime) / 1000)
                    device.emit_click(KEY_MAP[pressedChar],0)

                timing.append({
                    "key-char": pressedChar,
                    "keystroke-time": time.time_ns()
                })
                device.emit_click(KEY_MAP["SHIFT"],0)

            else:
                device.emit_click(KEY_MAP[pressedChar])
                timing.append({
                    "key-char": pressedChar,
                    "keystroke-time": time.time_ns()
                })
            time.sleep(interval / 1000)

            



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
    timing = []
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--real", action="store_true", default=False, help="real keystroke mode"
    )
    args = parser.parse_args()
    if not args.real:
        with mp.Manager() as manager:
            keypresses = manager.list()
            keyreleases = manager.list()
            print("make clean")
            os.system("make clean")
            print("make")
            os.system("make")
            print("sudo insmod spy.ko")
            print("Please start typing into any window: ")
            p = mp.Process(target=install_mod)
            q = mp.Process(target=simulate)
            p.start()
            q.start()
            p.join()
            stop_event.set()
            q.join()
    
            uninstall_mod()
    
            # Capture dmesg output
            output = os.popen("sudo dmesg -c").read().strip().split("\n")
            data = graph.sort_output(output)

            # """
            # Because simulated keys from pynput does not trigger keylogger, we will need to log the inputs by ourselves
            # """
    
            # data["keypresses"] = [
            #     {
            #         "key-char": key["key-char"],
            #         "keystroke-time": key["time"] - data["start_time"],
            #     }
            #     for key in keypresses
            #     if key["time"] > data["start_time"]
            # ]
    
            # data["keyreleases"] = [
            #      {
            #          "key-char": key["key-char"],
            #          "keystroke-time": key["time"] - data["start_time"],
            #      }
            #      for key in keyreleases
            #      if key["time"] > data["start_time"]
            #  ]
            
            for i in timing:
                 if timing["time"] > data["start_time"]:
                     data["keypresses"].append(
                     {
                         "key-char": i["key-char"],
                         "keystroke-time": i["keystroke-time"] - data["start_time"]
                     }
                     )
                  
                 
                 #TODO: Validate if start-time is the same
            graph.write_output(data)
            graph.graph_keystrokes(data)
    else:
        install_mod()
        test()
        uninstall_mod()
        output = os.popen("sudo dmesg -c").read().strip().split("\n")
        data = graph.sort_output(output)
        graph.write_output(data)
        graph.graph_keystrokes(data)
