# LLC Browser Prime+Probe Attack
This is a proof of concept for LLC Prime+Probe attack to extract keystroke timings from the browser. The codebase was based off spook.js and we include the original spook.js documentation regarding third party codebases. 

## System Setup 
- Disable prefetchers: ```wrmsr 0x1A4 0xf -a```
- Enable transparent hugepages: ```echo always | sudo tee /sys/kernel/mm/transparent_hugepage/enabled  && echo always | sudo tee /sys/kernel/mm/transparent_hugepage/shmem_enabled  && echo always | sudo tee /sys/kernel/mm/transparent_hugepage/defrag```
- Enable hugepages: echo 100 | sudo tee /proc/sys/vm/nr_hugepages
- CPU frequency settings: ```echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils```

## Running
The code uses node.js to run the webserver. We assume your system has node.js and npm installed. Run the following commands in this directory to start the server:
```
$ npm install
$ node ./server.js
```
A webserver would be launched at http://localhost:8080. 

## Third Party Code
Builds upon the following software:
- https://github.com/cgvwzq/evsets
- https://github.com/google/security-research-pocs

Third party code located in:
- static/js/leaky-page/
- static/js/evsets/

