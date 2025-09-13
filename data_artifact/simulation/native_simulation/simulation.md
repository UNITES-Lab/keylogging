### Simulation Instruction and Workflow
1. Place raw data into simulation/data/raw_data 
2. in simulation/data run clean.py, the cleaned data will be placed in simulation/data/cleaned_data
3. You can now start the simulation in one of the following ways 
	1. Go to /simulation and run ```./start_simulation```, this will setup the environment and print the outputs of both threads to the same terminal window
	2. If you would like to separately run 2 threads 
		1. setup the environment with ```./start_simulation```, you may kill the process immediately after you saw the search of eviction sets 
		2. in prime_probe, run ```sudo ./bin/test.out``` on window
		3. in prime_probe, run ```sudo python3 simulation/py/automate/simulate.py [speedup] [filename] [id]```
			1. the parameters are optional
			2. if you would like to use filename to specify a single file, you must enter an id, 0 if you want to start from the beginning
***Note: Please pay attention to the total duration of the test and whether there are missing characters that are not mapped in keymap.py ***
