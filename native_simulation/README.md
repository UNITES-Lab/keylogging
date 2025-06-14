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

## Running the simulation

Move the raw jsonl file you want to simulate into `data/raw_data` folder

You can then start the simulation with the following scripts

`sudo ./run_simulation [simulation_file_name] [speedup]`

***Note: Paths in the python scripts are set relative to native-simulation folder***

## Visualize the traces
You can viasualize each collected traces by running the following command, `sentence_id` could be obtained from the binary conversion files. 

`python3 pysim/analyze.py [simulation_file_name] [sentence_id] [speedup]`

## File IO Directories
- `data/raw_data`: the raw files from the public drive 
- `data/cleaned_data`: the cleaned files into preferable list format
- `data/binary_data`: hits per ms obtained from the simulation
- `data/output_data`: the output json in the same format for analysis 
- `figures`: all figures generated from `pysim/analyze.py`


