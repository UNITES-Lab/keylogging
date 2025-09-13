# Artifacts for KeyTAR: Practical Keystroke Timing Attacks and Input Reconstruction

This repository includes the side channel simulation system, ground truth and side channel data, and LLM analyses code for KeyTAR: Practical Keystroke Timing Attacks and Input Reconstruction. The organization is as follows: 

- data_artifacts: include the data collected from cache side channel attacks and the simulation system
    - data: the data folder contains the data we collected from experiments and used for analysis; the data files were zipped due to its large volume
        - websim_data: data collected in simulations run from the browser
        - nativesim_data: data collected in simulations run on the native environment
        - raw_data: initial data collected by Dhakal et. al. in their experiments collecting 136m keystrokes

    - simulation: codebase for running cache side-channel attacks 
        - web-simulation: contains the instructions, code, and scripts for running the browser attack
        - native-simulation: contains the instructions, code, and scripts for running the native attack

## TODO: Add readme for introducing ML codebase
