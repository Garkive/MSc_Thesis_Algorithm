# -*- coding: utf-8 -*-
"""
Created on Wed Aug 16 16:54:41 2023

@author: João Paulo
"""

from collections import deque
import timeit

def insert_into_list(lst, value, index):
    lst.insert(index, value)

def insert_into_deque(deq, value, index):
    deq.insert(index, value)

route = [22, 70838, 70835, 70660, 70662, 70670, 70658, 70653, 70662, 70660, 70835, 70653, 70658, 70812, 70818, 70822, 70670, 70822, 70818, 70830, 70812, 70838, 70666, 70666, 70830, 22]
route2 = deque(route)
value = 12345
index = 5

# Timing insertions in a list
list_time = timeit.timeit("insert_into_list(route, value, index)", globals=globals(), number=10000)

# Timing insertions in a deque
deque_time = timeit.timeit("insert_into_deque(route2, value, index)", globals=globals(), number=10000)

print(f"Insertion time in list: {list_time:.6f} seconds")
print(f"Insertion time in deque: {deque_time:.6f} seconds")
