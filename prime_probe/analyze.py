import numpy as np
import pandas as pd
from scipy import signal
from dtaidistance import dtw
from dtaidistance import dtw_visualisation

pp_values = np.fromfile("pp_keystrokes.bin", dtype=np.uint64)
kl_values = np.fromfile("kl_keystrokes.bin", dtype=np.uint64)

print(pp_values)
print(kl_values)

pp_values = ((pp_values - pp_values[0]) / (3.4 * 1000000)).astype(int) 
kl_values = ((kl_values - kl_values[0]) / (3.4 * 1000000)).astype(int)

# kl_values = kl_values - kl_values[1]
# pp_values = pp_values - kl_values[1] ##remove if cpu clocks aren't synced

#additional analysis by D

count = np.zeros(20000, dtype=int)
accurates = []
grouped = []
filtered = []

sorted_timestamps = np.sort(pp_values)
sorted_truths = np.sort(kl_values)

filtered = np.where(count >= 40)[0]         #change this value to adjust threshhold per noise, default is 75 counts


for v in sorted_timestamps:
    count[v] += 1

filtered = []
for i in range(10000):
    if count[i] > 100:
       filtered.append(i) 



sorted_timestamps = np.sort(pp_values)
sorted_truths = np.sort(kl_values)

filtered = np.where(count >= 60)[0]         #change this value to adjust threshhold per noise, default is 75 counts


#grouping function
prev = filtered[0]
grouped.append(filtered[0])
for v in filtered:
    if(v-prev > 0):          #change this value to adjust threshhold, default is 10ms
        grouped.append(v)
    prev = v



#determining normalization factor, find mathcing interval pattern, consider using DTW or measureing the difference in start time in two modules, latter is probably better




diff_pp = np.diff(grouped)
diff_truth = np.diff(sorted_truths) 

diff_pp_cleaned = list(filter(lambda a: a != 1, diff_pp))

diff_pp_cleaned = np.array(diff_pp_cleaned)

    #accuracy calculation with +-
prev = 0
for k in diff_truth:
    for v in diff_pp_cleaned[prev:10 + prev]:
        prev += 1
        if (abs(k-v) < 5):            #change this value to adjust threshhold, default is +-5ms
            accurates.append(v)
            break


    

print(diff_pp_cleaned)
print(diff_truth)
print(accurates)

# #accuracy calculation with +-
# for k in diff_truth:
#     for v in diff_pp:
#         if (abs(k-v) < 5):            #change this value to adjust threshhold, default is +-5ms
#             accurates.append(v)
#             continue
# print(sorted_truths)
# print(len(sorted_truths))
# print(accurates)

#interval calculation

print("Accuracy: " + str((len(accurates)/len(diff_pp_cleaned[3:15]))))
print("F-value: " + str(np.var(diff_pp_cleaned[3:15])/np.var(diff_truth[1:])))


corr = signal.correlate(diff_truth[1:], diff_pp_cleaned[3:15], mode='valid')

bestMatch = np.argmax(corr)

print("Best matching starting index:", bestMatch)

print("DTW Distance: ", dtw.distance(diff_truth[1:], diff_pp_cleaned[3:15]))
dtw_visualisation.plot_warping(diff_truth[1:], diff_pp_cleaned[3:15], dtw.warping_path(diff_truth[1:], diff_pp_cleaned[3:15]), filename="warp.png")

grouped = pd.Series(diff_pp_cleaned).rolling(window=5, center=True).mean()

print("Correlation Coefficient: " + str(grouped.corr(pd.Series(sorted_truths[1:]))))
#End D's Analysis      

print(pp_values)
print(len(kl_values)-2)
print(kl_values[1:-1])
