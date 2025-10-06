import numpy as np


a = np.arange(10,70,10)
results = np.split(a, [2, 3, 4])
print(a)
print(results)