# Flush+Reload Keystorke Timing Kernel Module 
### Before you begin 
1. Make sure you install all the relevant python libraries
2. Make sure you modify Makefile to use the right gcc version that your kernel is compiled with

### Simulation Mode 
1. Find the address of function you want to track **Please make sure you do this everytime you reboot as KASLR (Kernel Address Space Layout Randmization) will put functions to different locations**

```
sudo cat /proc/kallsyms | grep func_addr
```

```kbd_keycode``` yields the best result. 

Other candidates are
1. uinput_write 
2. ps2_interrupt
3. hid_keyboard

2. Modify the address in spy.c
3. Run execute.py to obtain graphs *make sure you complete step 1 & 2 and close gvim before you proceed*

```
sudo python3 execute.py
```

***Keylogger will not be in effect under simulation mode***

### Real Keystroke Mode
1. Repeat step 1 and 2 above with the flag --real
2. Type the keystrokes *the installation of the module is when the flush_reload period starts*

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
