# LLC Browser Prime+Probe Attack
This is a proof of concept for LLC Prime+Probe attack to extract keystroke timings from the browser. The codebase was based off spook.js and we include the original spook.js documentation regarding third party codebases. 

## System Setup 
- Disable prefetchers: ```wrmsr 0x1A4 0xf -a```
- Enable transparent hugepages: ```echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled  && echo always | sudo tee /sys/kernel/mm/transparent_hugepage/shmem_enabled  && echo always | sudo tee /sys/kernel/mm/transparent_hugepage/defrag```
- Enable hugepages: echo 100 | sudo tee /proc/sys/vm/nr_hugepages
- CPU frequency settings: ```echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils```
- Disable c-state: set `intel_idle.max_cstate =0` in /etc/default/grub

## Running the simulation
Before running the simulation, please ensure that your system is as quiet as possible with limited background processes running as this may affect the quality of your simulated results. 

You will need to create the *traces* directory to in spookjs-poc-main for storing the binaries. Failing to do this will result in deadlock situation since the system will never be ready again after processing the first trace. 

The code uses node.js to run the webserver. We assume your system has node.js and npm installed. Run the following commands in this directory to start the server:
```
$ npm install
$ node ./server.js
```
A webserver would be launched at http://localhost:8080. 

Next, please proceed with launching the browser. We recognize that the eviction set reduction algorithm failed typically on the first run, please refresh the page until you see 8 sets found on the display screen. 

Last, you may now run `sudo python3 simulate.py` from the *pysim* directory. The simulation will start automatically. Please ensure that you avoid using your keyboard, mouse, or external devices to minimize potential noise on the system. 

## Third Party Code
Builds upon the following software:
- https://github.com/cgvwzq/evsets
- https://github.com/google/security-research-pocs

Third party code located in:
- static/js/leaky-page/
- static/js/evsets/

