# Flush+Reload Keystorke Timing Kernel Module 
### Before you begin 
1. Make sure you install all the relevant python libraries
2. Make sure you modify Makefile to use the right gcc version that your kernel is compiled with

### Using the Tool 
1. Find the address of kbd_keycode. ***You only have to do this once per reboot***

```
sudo cat /proc/kallsyms | grep kbd_keycode
```

2. Modify the address (FUNCTION_ADDRESS) in spy.c
3. Run execute.py with sudo privilege

```
sudo python3 execute.py
```

4. Start typing when prompted to on the screen

After the code had finished execution (or you have completed the manual steps), you can close the gvim terminal. Below will be the descriptions of the files. ***Note: keylogger files are only available during real keystroke mode, key press and release files are only available during simulation keystroke mode***
1. flush_reload.png: The graph of cache hits with respect to time
2. filtered_flush_reload.png: filter result of flush+reload
3. keypresses.png: The graph of key presses with respect to time 
4. keyreleases.png: The graph of key releases with respect to time
5. krfr.png: keyrelease graph overlaid on flush+reload
6. kpfr.png: keypress graph overlaid on flush+reload 
7. kpffr.png: keypress graph overlaid on filtered flush+reload
8. krffr.png: keypress graph overlaid on filtered flush+reload
10. flush_reload.json: the data used in the flush_reload graph
11. keypresses.json: the data used in keypress graph
12. keyreleases.json: the data used in keyreleases graph
