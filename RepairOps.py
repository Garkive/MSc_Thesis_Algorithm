# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 14:49:15 2023

@author: João Paulo
"""
import copy
#Find costumer number from Pickup+Delivery id number
def find_pos(i_d, points):    
    pos = [i for i,x in enumerate(points['id']) if x==i_d]    
    return pos
#Find id number of a Pickup or Delivery
def find_id(pos, points):
    i_d = points.iloc[pos]['id']
    return i_d

    
    
    
    
    return feasible #True or Fals   
#Calculates Total Route Cost (Considers only distance)
def route_cost(route, dist_mat):
    Auxiliary_list = []
    rcost = 0
    for i in range(len(route)-1):
        if route[i] in Auxiliary_list and i != 0:
            p1 = find_pos(route[i], points)[1]
        else:
            p1 = find_pos(route[i], points)[0]
            Auxiliary_list.append(route[i])
        if route[i+1] in Auxiliary_list and i+1 != len(route)-1:
            p2 = find_pos(route[i+1], points)[1]
        else:
            p2 = find_pos(route[i+1], points)[0]
        print('Point 1: ',p1)
        print('Point 2: ',p2)
        rcost += dist_mat[p1][p2]
    return rcost
#Calculates Total Solution Cost (Using route_cost function)
def solution_cost(solution, dist_mat):
    scost = 0
    for hub_routes in solution:
        for route in hub_routes:
            rcost = route_cost(route,dist_mat)
            scost += rcost
    return scost 
def insertion_cost(route, costumer, dist_mat, k):
    return 
#Feasibility of Insertion (yet to be made)
def feasibility_check(pos, k, route, P_or_D, data, points):
    return
    return
#Greedy Insertion Repair Operator   
def Greedy_Insertion(hub_num, removed_req, partial_solution, points): #Until all requests are inserted 

    for costumer in removed_req:
        insertcost_list = []
        for i in range(hub_num):
            for route_ind, route in enumerate(partial_solution[i]):
                for j in range(1,len(route)-1):
                    temp_route_p = copy.deepcopy(route)
                    temp_route_p.insert(j, find_pos(costumer, points)[0])
                    for k in range(j+1, len(route)-1):
                        icost = insertion_cost(temp_route_p, costumer, dist_mat, k)
                        insert_index = []
                        insertcost_list.append()
                        temp_route_d = temp_route_p.insert(k, find_pos(costumer, points)[1])
                        




    for i in hub_num:
        for j in partial_solution[i]:
            for k in D:
                P_or_D = 'Pickup'
                for pos in range(1,len(partial_solution[i][j])-1):
                    feasible = feasibility_check(pos, k, partial_solution[i][j])
                    
                    
            
            
            
            
            
            
            
    return 