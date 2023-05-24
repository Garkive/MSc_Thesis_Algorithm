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

#Calculates Total Route Cost (Considers only distance)
def route_cost(route, dist_mat, points):   
    #DISTANCE
    Auxiliary_list = []
    rcost = 0
    for i in range(len(route)-1):
        #print('Route :', route)
        #print('Route 1: ', route[i])
        #print('Route 2: ', route[i+1])
        if route[i] in Auxiliary_list and i != 0:
            p1 = find_pos(route[i], points)[1]
        else:
            p1 = find_pos(route[i], points)[0]
            Auxiliary_list.append(route[i])
        if route[i+1] in Auxiliary_list and i+1 != len(route)-1:
            p2 = find_pos(route[i+1], points)[1]
        else:
            p2 = find_pos(route[i+1], points)[0]
        #print('Point 1: ',p1)
        #print('Point 2: ',p2)
        rcost += dist_mat[p1][p2]
        
    return rcost

#Calculates Total Solution Cost (Using route_cost function)
def solution_cost(solution, dist_mat, points):
    scost = 0
    for hub_routes in solution:
        for route in hub_routes:
            rcost = route_cost(route,dist_mat, points)
            scost += rcost
    return scost 

#Calculates Cost of Inserting Request in Route
def insertion_cost(route, rcost, dist_mat, points): 
    newrcost = route_cost(route, dist_mat, points)
    insertcost = newrcost - rcost
    return insertcost

#Feasibility of Insertion 
def feasibility_check(route, data, points, dist_mat):
    
    
    
    feasible = True
    Auxiliary_list = [] #List to keep track of pickup or delivery
    current_weight = 0
    current_volume = 0
    current_time = 0
    
    #These values depend on choice or vehicle
    weight_limit = 30
    volume_limit = 3000000
    service_time = 10
    veh_spd = 15
    
    for i in range(1, len(route)-1):
        
        if i != len(route)-1:
            #Weight Constraint (Considers van only)
            if current_weight + data['weight'][route[i]] > weight_limit:
                feasible = False
                break
            else:
                current_weight += data['weight'][route[i]]
                
            #Volumetric Constraint (Considers van only)
            if current_volume + data['volume'][route[i]] > volume_limit:
                feasible = False
                break
            else:
                current_volume += data['volume'][route[i]]
                
        if route[i-1] in Auxiliary_list and i-1 != 0:
            p1 = find_pos(route[i-1], points)[1]
        else:
            p1 = find_pos(route[i-1], points)[0]
            Auxiliary_list.append(route[i-1])
        if route[i] in Auxiliary_list and i != len(route)-1:
            p2 = find_pos(route[i], points)[1]
            s_time = 'start_time_do' 
        else:
            s_time = 'start_time_pu' 
            p2 = find_pos(route[i], points)[0]
            
        #Time Constraint (relaxed, considers van only)
        if current_time + dist_mat[p1][p2]/veh_spd > data[s_time].loc[find_id(p2,points)]:
            current_time = current_time + dist_mat[p1][p2]/veh_spd + service_time 
        else:
            current_time = data[s_time].loc[find_id(p2,points)] + service_time
            #Can add wait time in the future
            
    return feasible

    return
#Greedy Insertion Repair Operator   
def Greedy_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat): #Until all requests are inserted 

    for costumer in removed_req:
        insert_list = []
        cost_list = []
        for i in range(hub_num):
            for route_ind, route in enumerate(partial_solution[i]):
                rcost = route_cost(route, dist_mat, points)
                for j in range(1,len(route)-1):
                    temp_route_p = copy.deepcopy(route)
                    temp_route_p.insert(j, costumer)
                    is_feasible = feasibility_check(temp_route_p, data, points, dist_mat)
                    if is_feasible == False:
                        continue
                    else:
                        for k in range(j+1, len(route)-1):
                            temp_route_d = copy.deepcopy(temp_route_p)
                            temp_route_d.insert(k, costumer)
                            is_feasible = feasibility_check(temp_route_d, data, points, dist_mat)
                            if is_feasible == False:
                                continue
                            else:
                                icost = insertion_cost(temp_route_d, rcost, dist_mat, points)
                                insert_index = [i, route_ind, j, k]
                                insert_list.append(insert_index)
                                cost_list.append(icost)
        index = cost_list.index(min(cost_list))
        partial_solution[insert_list[index][0]][insert_list[index][1]].insert(insert_list[index][2], costumer)
        partial_solution[insert_list[index][0]][insert_list[index][1]].insert(insert_list[index][3], costumer)
                 
    return partial_solution

# def RepairOperator():
#   newsol = Greedy_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat)
#   return
#solution = Greedy_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat)