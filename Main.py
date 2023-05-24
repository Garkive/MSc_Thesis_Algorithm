# -*- coding: utf-8 -*-
"""
Created on Wed May 24 10:27:38 2023

@author: João Paulo
"""

import DestroyOps
import RepairOps
import time

max_iter = 10
time_limit = 20 #seconds

points, data, dist_mat, hub_num, routes, indices = DestroyOps.import_data()
solution = DestroyOps.display_routes(routes)
id_list, solution_id = DestroyOps.solution_ids(solution, points)

# n = len(indices)-hub_num #Number of pickup delivery pairs
# d = 0.3 #Degree of destruction
# q = round(n*d) #Number of pairs to be removed each iteration

# #Shaw Removal parameters
# p = 5 #Introduces randomness in selection of requests
# phi = 5#Weight of distance in relatedness parameter
# xi = 3#Weight of time in relatedness parameter
# qsi = 2#Weight of demand in relatedness parameter

start_time = time.time()
current_time = 0
current_iter = 1
current_sol = solution_id
current_sol_cost = RepairOps.solution_cost(current_sol, dist_mat, points)

while current_iter <= max_iter and current_time < time_limit:
    
    current_time = time.time() - start_time
    
    partial_solution, removed_req, solution_id = DestroyOps.DestroyOperator()
    newsol = RepairOps.Greedy_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat)
    
    newsol_cost = RepairOps.solution_cost(newsol, dist_mat, points)
    
    if newsol_cost <= current_sol_cost:
        current_sol = newsol
    
    current_iter += 1
    
best_sol = current_sol
best_sol_cost = RepairOps.solution_cost(best_sol, dist_mat, points)
    
print('Cost of final solution is: ', best_sol_cost)