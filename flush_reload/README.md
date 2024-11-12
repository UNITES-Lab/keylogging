# Flush+Reload Keystorke Timing Kernel Module 

1. Find the address of function you want to track

```
sudo cat /proc/kallsyms | grep func_addr
```

2. Modify the address in spy.c
3. Run execute.py to obtain graphs *make sure you complete step 1 & 2 and close gvim before you proceed*

```
sudo python3 execute.py
```
### Note: Currently the script only supports simulated keystrokes of keys at fixed intervals, if you would like to test it manually, please follow the instructions below 

1. Repeat step 1 and 2 above
2. Compile the code 
```
make
```
3. Install the kernel module
```
sudo insmod spy.ko
```
4. Type the keystrokes *the installation of the module is when the flush_reload period starts*
5. Remove the kernel module
6. Copy the kernel log into logs/test.log or your desired location **if you place at your desired location, make sure to modify graph.py**
```
sudo dmesg -c >> logs/test.log
```
7. run graph.py to obtain the graphs and results 
```
python3 graph.py
```

After the code had finished execution (or you have completed the manual steps), you can close the gvim terminal. Below will be the descriptions of the files
1. flush_reload.png: The graph of cache hits with respect to time
2. keylogger.png: The graph of key hit with respect to time
3. filtered_flush_reload.png: filter result of flush+reload overlaid on keylogger for evaluation of prediction 
4. keylogger.json: data used in the keylogger graph 
5. flush_reload.json: the data used in the flush_reload graph

### All time measurements are in nanoseconds (ns)
