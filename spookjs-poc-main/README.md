# LLC Browser Prime+Probe Attack
This is a proof of concept for LLC Prime+Probe attack to extract keystroke timings from the browser. The codebase was based off spook.js and we include the original spook.js documentation regarding third party codebases. 

## System Setup 

First setup grub and restart to turn off pstate and cstate

```
chmod +x *
sudo ./update_grub.sh
sudo reboot
```

Turn off prefetchers, set frequency and enable hugepages

```
sudo ./setup_system.sh
```

Setup required simulation folder
```
./setup_simulation.sh
```

## Running the simulation

Move the raw jsonl file you want to simulate into `data/raw_data` folder

Start the server with sudo access to write to file 

`sudo node server.js`

Please start Google Chrome Browser and go to http://localhost:8080 (restart the page until you find 8 eviction sets)

You can then start the simulation with the following scripts

`sudo ./run_simulation [simulation_file_name.jsonl]`

***Note: Paths in the python scripts are set relative to web-simulation folder***

## Visualize the Simulation
You can viasualize each collected traces by running the following command, `sentence_id` could be obtained from the binary conversion files. 

`python3 pysim/anaylyze.py [sentence_id]`

## Third Party Code
Builds upon the following software:
- https://github.com/cgvwzq/evsets
- https://github.com/google/security-research-pocs

Third party code located in:
- static/js/leaky-page/
- static/js/evsets/

