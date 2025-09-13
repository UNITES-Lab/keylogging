# KeyTAR
KeyTAR is a keystroke timing extraction and inference framework that demonstrates the feasibility of reconstructing user input using only inter-keystroke timing information. While side-channel researchers have long speculated about the potential for such reconstruction, KeyTAR shows the vulnerability is real through accurate keystroke inferences with Large Language Models (LLM).

The attack consists of two main components:

1. Keystroke Extraction: Collects inter-keystroke timings through microarchitectural side-channel techniques.

2. Keystroke Inference: Uses the extracted timings to infer the original typed input.

This directory contains the **keystroke extraction** portion of the attack.

### ./native_simulation and ./web-simulation
These directories include tools for simulating Prime+Probe attacks in native and web environments, respectively. They support replaying keystrokes using our public dataset. Please see the README in each folder for setup and execution details.

### Attack Environment
We modify the parameters to perform the attack on a Sandy Bridge (i7-2600) and use the hardware settings outlined in setup-system.sh in each simulation folder. We have observed similar successes on other later architectures (Kaby Lake) with their respective parameters. 
