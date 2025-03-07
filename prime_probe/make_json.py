import json
import numpy as np


values = np.fromfile("/prime_probe/kl_keystrokes.bin", dtype=np.uint64) 
print(values)


