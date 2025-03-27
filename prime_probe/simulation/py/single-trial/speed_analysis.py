import os
import numpy as np

SPEED_UP = 3  # Set this to 1 for 1x speed or 10 for 10x speed

data_dir = "output_binary/test"
files = os.listdir(data_dir)

# Lists to accumulate statistics for each file
all_means = []
all_variances = []
all_std = []
total_count = 0

CPU_FREQ = 3.4  
conversion_factor = 3.4e6

for file in files:
    file_path = os.path.join(data_dir, file)
    values = np.fromfile(file_path, dtype=np.uint64)
    if values.size == 0:
        print(f"File {file_path} is empty, skipping.")
        continue
    timestamps = ((values - values[0]) / conversion_factor) * SPEED_UP
    timestamps = timestamps.astype(int)
    
    file_mean = np.mean(timestamps)
    file_var = np.var(timestamps)
    file_std = np.std(timestamps)
    
    all_means.append(file_mean)
    all_variances.append(file_var)
    all_std.append(file_std)
    
    total_count += len(timestamps)

overall_mean = np.mean(all_means)
overall_var = np.mean(all_variances)
overall_std = np.mean(all_std)

print("Speed-up:", SPEED_UP)
print("Total count of values:", total_count)
print("Overall mean timestamp (ms):", overall_mean)
print("Overall variance:", overall_var)
print("Overall standard deviation:", overall_std)
