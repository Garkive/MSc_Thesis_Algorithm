#Multiprocessing attempt for multiple runs of the algorithm in parallel

import multiprocessing
import subprocess

# Module/script name to execute
module_name = 'Main.py'  # Replace with the name of your module

# Number of CPU cores to utilize
num_cores = multiprocessing.cpu_count()

# Function to execute a module
def execute_module(module_name):
    subprocess.call(['python', '-m', module_name])

# Create a multiprocessing Pool with the number of CPU cores
pool = multiprocessing.Pool(processes=num_cores)

# Map the execute_module function to the list of module names
pool.map(execute_module, [module_name] * num_cores)

# Close the multiprocessing Pool
pool.close()
pool.join()