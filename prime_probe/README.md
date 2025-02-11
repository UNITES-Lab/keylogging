# Acknowledgements
This code builds on eviction-sets developed by Max Christman and extends to a full prime+probe attack recovering keystroke timing. 

# How to launch the attack?

### Setup
1. If you just restarted / turn on your computer, check if you have huge pages set up 

```
grep -i huge /proc/meminfo
```

2. If you do not, set up huge pages 

```echo NUM_PAGES | sudo tee /proc/sys/vm/nr_hugepages```

3. Find the virtual address of kbd_keycode in your system and copy the address to v2p_kernel/v2p.c and replace the value in my_module_init, func_addr

```sudo cat /proc/kallsyms | grep kbd_keycode```

4. Convert the virtual address to physical address using the kernel module

```sudo insmod v2p.ko```

If your system shows a warning referring to certificates not being signed, please go into bios and enter insecure mode 

5. View the physical address 
```sudo dmesg```

6. Copy the physical address to replace the address in src/test.c KBD_KEYCODE

### Running the code 

```sudo ./attack.sh```

If the logs show that we fail to generate the eviction sets for all slices, please try again. 

### Operation Modes 
- The default mode runs with probing all slices of set 428
- If you only want to probe the target slice, change the following items 
1. modify src/test.c to use ```prime_probe``` instead of ```prime_probe_many_sets```
2. uncomment line 82 and comment out line 83 and line 84 

# Critical Notes 
1. Hugepages are used
2. isolcpus, nohz_full, and cpuset is set on cpu 0 on Everglades

# Optional Settings

### Isolate CPU 
1. GRUB_CMDLINE_LINUX_DEFAULT="isolcpus=1,2" 
2. sudo update-grub; 
3. sudo reboot 
4. cat /proc/cmdline

### Create CPU set
```sudo cset shield --cpu=0 --kthread=on```

### Run on CPU set
```sudo cset shield --exec ./your_program```

#Disable Prefetchers: 
### **1. Install the `msr-tools` Package**
On Linux, you need the `msr-tools` package to read and write MSRs.

#### For Debian/Ubuntu:
```bash
sudo apt update
sudo apt install msr-tools
```

#### For RHEL/CentOS/Fedora:
```bash
sudo yum install msr-tools
```

---

### **2. Load the `msr` Kernel Module**
The `msr` kernel module must be loaded to allow access to the MSRs.

```bash
sudo modprobe msr
```

To verify it is loaded:
```bash
lsmod | grep msr
```

---

### **3. Identify the MSR for Prefetch Control**
The control for hardware prefetchers is typically located in the **MSR 0x1A4** (Intel processors). The value written to this register controls the state of various prefetchers.

- **Bits to control specific prefetchers:**
  - **Bit 0**: Disable L2 hardware prefetcher.
  - **Bit 1**: Disable adjacent cache-line prefetcher.
  - **Bit 2**: Disable DCA prefetcher.
  - **Bit 3**: Disable L1 hardware prefetcher.

A value of `0xF` disables all prefetchers.

---

### **4. Write to the MSR**
You need to write the desired value to the MSR register for each CPU core. For example:

#### Disable all prefetchers (write `0xF`):
```bash
sudo wrmsr -p <CPU_ID> 0x1A4 0xF
```

- `<CPU_ID>`: The ID of the CPU core (starting from `0`). Use a loop to write to all cores.

#### Example: Disable on all cores
```bash
for cpu in $(seq 0 $(nproc --all)); do
    sudo wrmsr -p $cpu 0x1A4 0xF
done
```

#### Verify:
You can verify the setting with:
```bash
sudo rdmsr -p <CPU_ID> 0x1A4
```

---

### **5. Automate on Boot**
To apply these settings at boot:
1. Create a script to execute the commands.
2. Place the script in `/etc/init.d/` or create a systemd service.

Example script:
```bash
#!/bin/bash
for cpu in $(seq 0 $(nproc --all)); do
    wrmsr -p $cpu 0x1A4 0xF
done
```

Make it executable:
```bash
chmod +x /path/to/your/script.sh
```

---
