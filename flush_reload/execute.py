import time
import json
import os
from pynput.keyboard import Controller
import signal  # handle sigsegv
import argparse
import multiprocessing as mp
import graph

stop_event = mp.Event()


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
    os.system("sudo insmod spy.ko")


def start_keystrokes():
    keyboard = Controller()

    print("gvim")
    os.system("gvim")

    print('xdotool search --name "gvim"')
    window_id = os.popen('xdotool search --name "gvim"')
    print(f"xdotool windowactivate {window_id}")
    os.system(f"xdotool windowactivate {window_id}")

    start_time = time.time_ns()
    print(f"keystroke starts: {start_time}")

    # Modify this code to simulate the keystroke patterns you want to automate
    while not stop_event.is_set():
        keyboard.press("a")
        keypresses.append({"key-char": "a", "time": time.time_ns()})
        time.sleep(0.05)  # hold key for 100 ms
        keyboard.release("a")
        keyreleases.append({"key-char": "a", "time": time.time_ns()})
        time.sleep(0.2)  # wait for 200 ms before next press


def uninstall_mod():
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
            q = mp.Process(target=start_keystrokes)
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
        print("please start typing: ")
        uninstall_mod()
        output = os.popen("sudo dmesg -c").read().strip().split("\n")
        data = graph.sort_output(output)
        graph.write_output(data)
        graph.graph_keystrokes(data)
