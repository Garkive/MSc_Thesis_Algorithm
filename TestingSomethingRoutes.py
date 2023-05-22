# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 12:47:58 2023

@author: João Paulo
"""

def display_routes(routes): 
     solution = []
     for i in range(len(routes)):
         hub_sol = []
         route_sol = []
         start_route = True
         print('i: ',i)
         for j in range(len(routes[i])):
             print(route_sol)
             print('j: ',j)
             if routes[i][j] == i and start_route == False:
                 route_sol.append(i)
                 hub_sol.append(route_sol)
                 route_sol = []
                 start_route = True
             if start_route:
                 route_sol.append(i)
                 start_route = False
             else:
                 route_sol.append(routes[i][j])
         solution.append(hub_sol)
     return solution
def solution_ids(solution, points):
    hub_ids = []
    id_list = []
    for i in range(len(solution)):
        hub_ids.append(find_id(i, points))
        for j in range(len(solution[i])):
            id_nums = [find_id(x,points) for x in solution[i][j]]
            for k in range(len(id_nums)):
                if id_nums[k] not in id_list and id_nums[k] not in hub_ids:
                    id_list.append(id_nums[k])
    return id_list