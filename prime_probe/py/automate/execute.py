import time
import json
import os
import signal  # handle sigsegv
import argparse
import multiprocessing as mp
import numpy 
import sys
import uinput
import subprocess
import threading
import simulate



stop_event = mp.Event()


def get_address(func: str) -> str:
    output = os.popen(f"sudo cat /proc/kallsyms | grep {func}").read().strip()
    return output


def handle_signal(signum, frame):
    exit(0)


def setup_shell():
    os.system("sudo ./attack.sh")

def install_mod():
    print("sudo insmod spy.ko")
    os.system("sudo insmod ./keylogger/spy.ko")
    os.system("cd /home/dohhyun/keylogging/keylogging/prime_probe")

def uninstall_mod():
    print("sudo rmmod spy.ko")
    os.system("sudo rmmod spy.ko")

def plot():
    import plot
    subprocess.call(['python3', 'plot.py'])

def analyze():
    import analyze
    subprocess.call(['python3', 'analyze.py'])


#TODO:pass start time to plot.py

if __name__ == "__main__":
    
    setup_shell()
    process = subprocess.Popen(["./bin/test.out"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, text=True)
    thread = mp.Process(target=simulate.simulate_json)
    keylogger = mp.Process(target=install_mod)
    for line in iter(process.stdout.readline, ''):
        print(line)
        if "please start typing" in line:
            keylogger.start()
            keylogger.join()
            thread.start()
    process.wait()
    thread.join()
    uninstall_mod()
    print("plotting...")
    plot()
    print("stats...")
    analyze()