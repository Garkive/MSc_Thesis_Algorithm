# -*- coding: utf-8 -*-
"""
Created on Sun Oct  8 17:43:56 2023

@author: João Moura
"""

from collections import deque
import RepairOps
import time 

my_deque = deque([(1854.1469999999972, 0, 2, 1, 6, 70666), (1235.3429999999935, 0, 2, 5, 9, 70830), (4731.205000000002, 0, 0, 1, 6, 70658), (13013.687999999995, 1, 1, 1, 3, 70822)])

min_entry = min(my_deque, key=lambda x: x[0])
print(min_entry)

time1 = time.time()
for i in range(1,1000):
    RepairOps.feasibility_check([22, 70840, 70830, 70838, 70835, 70838, 70840, 70830, 70835, 22], points2, inv_points2, dist_mat, data2)
print('Total Time: ', time.time()-time1)

time1 = time.time()
for i in range(1,100000):
    RepairOps.find_pos(70835, inv_points2)
print('Total Time: ', time.time()-time1)