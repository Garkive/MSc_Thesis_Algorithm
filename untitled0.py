# -*- coding: utf-8 -*-
"""
Created on Fri Jun  9 16:26:47 2023

@author: João Paulo
"""

import multiprocessing

def square(number):
    """Function to calculate the square of a number."""
    return number ** 2

if __name__ == '__main__':
    # List of numbers
    numbers = [1, 2, 3, 4, 5]

    # Create a multiprocessing pool with 3 processes
    pool = multiprocessing.Pool(processes=3)

    # Apply the square function to each number using the pool
    results = pool.map(square, numbers)

    # Close the pool to indicate that no more tasks will be submitted
    pool.close()

    # Wait for all the worker processes to finish
    pool.join()

    # Print the results
    print(results)