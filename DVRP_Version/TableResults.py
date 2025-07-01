# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 14:13:50 2024

@author: João Moura
"""
import numpy as np
sols = [2719.29,2704.57,2706.79,2705.43,2705.94]
times = [372.39,387.89,392.62,394.27,600.42,612.68]

avg_time = np.mean(times)
avg_sols = np.mean(sols)
std_dev = np.std(sols)
best_sol = min(sols)

print('Time avg.: ', avg_time)
print('Solution avg.: ', avg_sols)
print('Standard Deviation: ', std_dev)
print('Best Solution Found: ', best_sol)