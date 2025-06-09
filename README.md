# KeyTAR
KeyTAR is a keystroke timing extraction and inference framework that demonstrates the feasibility of reconstructing user input using only inter-keystroke timing information. While side-channel researchers have long speculated about the potential for such reconstruction, KeyTAR proves the vulnerability is real—leveraging Large Language Models (LLMs) to infer typed input from timing data alone.

The attack consists of two main components:

1. Keystroke Extraction: Collects inter-keystroke timings through microarchitectural side-channel techniques.

2. Keystroke Inference: Uses the extracted timings to infer the original typed input.

This repository contains the **keystroke extraction** portion of the attack.

### ./flush_reload
This directory contains a visualization tool for analyzing Flush+Reload side-channel traces against ground truth kernel function usage. Refer to the README inside the folder for detailed instructions and usage.

### ./native_simulation and ./web-simulation
These directories include tools for simulating Prime+Probe attacks in native and web environments, respectively. They support replaying keystrokes using our public dataset. Please see the README in each folder for setup and execution details.
