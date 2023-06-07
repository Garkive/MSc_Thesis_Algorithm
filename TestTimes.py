# -*- coding: utf-8 -*-
"""
Created on Mon May 29 08:44:52 2023

@author: João Paulo
"""
import timeit

def access_dataframe():
    value = data['start_time_do'].loc[70822]  # Accessing value from column 'A' and the first row

# Access operation on dictionary
def access_dictionary():
    value = data2['start_time_do'][70822]  # Accessing value from the dictionary

# Time the access operation on DataFrame
df_time = timeit.timeit(access_dataframe, number=100000)

# Time the access operation on dictionary
dict_time = timeit.timeit(access_dictionary, number=100000)

# Print the time taken for DataFrame access
print("Time taken for DataFrame access:", df_time)

# Print the time taken for dictionary access
print("Time taken for dictionary access:", dict_time)

-----------------------------------------------------------------------------------------------------

# Time the access operation on dictionary
dict_time = timeit.timeit(lambda: RepairOps.feasibility_check(partial_solution[0][0], points, dist_mat,data), number=1)

# Print the time taken for DataFrame access
print("Time taken for feasibility check:", dict_time)

-----------------------------------------------------------------------------------------------------

# Time the access operation on dictionary
dict_time = timeit.timeit(lambda: RepairOps.find_id(1, points), number=100000)

# Print the time taken for DataFrame access
print("Time taken for feasibility check:", dict_time)

-----------------------------------------------------------------------------------------------------

def access_distmat():
    value = dist_mat[20][1]

# Time the access operation on dictionary
dict_time = timeit.timeit(access_distmat, number=100000)

# Print the time taken for DataFrame access
print("Time taken for feasibility check:", dict_time)