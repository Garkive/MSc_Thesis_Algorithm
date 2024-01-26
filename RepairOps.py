#Repair operators development to be used in the ALNS framework

#Input - Partial Solution and List of Removed Requests by the Destroy Operators
#Output - New repaired solution

#Operators initially considered:
    #1 - Greedy Insertion
    #2 - Regret Insertion (Probably more than one type)
    
#Optimized data structures allow for fast computation and costumer insertion

import heapq
import OperatorSelection
""" import math """
import time
import random
from collections import deque

#Find costumer number from Pickup+Delivery id number
def find_pos(i_d,  inv_points):    
    pos = inv_points[i_d]
    return pos

#Find id number of a Pickup or Delivery
def find_id(pos, points):
    i_d = points['id'][pos]
    return i_d

def route_cost(route, dist_mat, points, inv_points, data, fleet, vehicle): 
    auxiliary_list = deque()
    rcost = 0
    total_tardiness = 0
    time = 0
    
    veh_spd = fleet['speed'][vehicle]
    service_time = 5 * 60
    
    # veh_spd = 1
    # service_time = 0
    
    for i in range(len(route)-1):
        p1 = find_pos(route[i], inv_points)[auxiliary_list.count(route[i])]
        auxiliary_list.append(route[i])
        
        if i+1 != len(route)-1:
            p2 = find_pos(route[i+1], inv_points)[auxiliary_list.count(route[i+1])]
            e_time = 'end_time_do'
            s_time = 'start_time_do'
        else:
            p2 = find_pos(route[i+1], inv_points)[0]
            e_time = 'end_time_pu'
            s_time = 'start_time_pu'
        
        travel_time = dist_mat[p1][p2] / veh_spd
        arrival_time = time + travel_time + service_time
        if i+1 != len(route)-1 and arrival_time > data[e_time][find_id(p2, points)]:
            tardiness = max(arrival_time - data[e_time][find_id(p2, points)], 0)
            total_tardiness += tardiness
            time = max(arrival_time, data[s_time][find_id(p2, points)] + service_time)
        else:
            time = arrival_time
            tardiness = 0
        rcost += dist_mat[p1][p2] + tardiness
    rcost = rcost*((fleet['cost_km'][vehicle]/1000)/100)
    return rcost

#Calculates Total Solution Cost (Using route_cost function)
def solution_cost(solution, dist_mat, points, inv_points, data, fleet, veh_solution):
    scost = 0
    # sol_tardiness = 0
    
    for i in range(len(solution)):
        for j in range(len(solution[i])):
            rcost = route_cost(solution[i][j], dist_mat, points, inv_points, data, fleet, veh_solution[i][j])
            scost += rcost
    
    # for hub_routes in solution:
    #     for route in hub_routes:
    #         rcost = route_cost(route,dist_mat, points, inv_points, data, fleet)
    #         scost += rcost
    return scost

#Calculates Cost of Inserting Request in Route
def insertion_cost(route, rcost, dist_mat, points, inv_points, data, fleet, veh_solution, vehicle): 
    newrcost = route_cost(route, dist_mat, points, inv_points, data, fleet, vehicle)
    insertcost = newrcost - rcost
    return insertcost

#Feasibility of Insertion 
def feasibility_check(route, points, inv_points, dist_mat, data, fleet, vehicle):
    feasible = True
    current_weight = 0
    current_volume = 0
    current_time = 0
    
    weight_limit = fleet['max_weight'][vehicle]
    volume_limit = fleet['capacity'][vehicle]
    veh_spd = fleet['speed'][vehicle]
    service_time = 10 * 60
    
    # weight_limit = 200
    # volume_limit = 0
    # veh_spd = 1
    
    for i in range(1, len(route) - 1):
        wait_time = 0
        if i-1 == 0:
            weight = float('nan')
            p1 = find_pos(route[i-1], inv_points)[0]
            p2 = find_pos(route[i], inv_points)[0]
        else:
            if route[i-1] in route[:i-1]:
                weight = -data['weight'][route[i-1]]
                volume = -data['volume'][route[i-1]]
                p1 = find_pos(route[i-1], inv_points)[1]
            else:
                weight = data['weight'][route[i-1]]
                volume = data['volume'][route[i-1]]
                p1 = find_pos(route[i-1], inv_points)[0]

        if route[i] in route[:i] and i != len(route) - 1:
            p2 = find_pos(route[i], inv_points)[1]
            s_time = 'start_time_do'
            e_time = 'end_time_do'
        else:
            s_time = 'start_time_pu'
            e_time = 'end_time_pu'
            p2 = find_pos(route[i], inv_points)[0]
        if weight != weight:
            feasible = True
        else: 
            if current_weight + weight > weight_limit or current_volume + volume > volume_limit:
                feasible = False               
                break
            else:
                current_weight += weight
                current_volume += volume   
        travel_time = dist_mat[p1][p2] / veh_spd
        arrival_time = data[s_time][find_id(p2, points)]   
        end_time = data[e_time][find_id(p2, points)]
        service_time = points['service_time'][p2]        
        if current_time + travel_time < arrival_time:
            wait_time = arrival_time - travel_time - current_time
        if current_time + travel_time + wait_time >= arrival_time and current_time + travel_time <= end_time:
            current_time += travel_time + service_time + wait_time
        else:
            feasible = False
            break
    return feasible

def create_route(costumer, dist_mat, indices, hub_num, points, inv_points, fleet, veh_solution, pheromone_mat):
    costumer_pos = find_pos(costumer, inv_points)
    dist = [float(dist_mat[indices[i][0]][costumer_pos[0]] + dist_mat[indices[i][0]][costumer_pos[1]]) for i in range(hub_num)]
    index = dist.index(min(dist))
    route = [find_id(indices[index][0], points), costumer, costumer, find_id(indices[index][0], points)]
    choice_v = OperatorSelection.vehicle_selection(route, pheromone_mat, inv_points)
    veh_solution[index].append(choice_v)
    return route, index, veh_solution

def new_route_insert_list(costumer, dist_mat, indices, hub_num, points, inv_points, data, fleet):
    costumer_pos = find_pos(costumer, inv_points)
    dist = [float(dist_mat[indices[i][0]][costumer_pos[0]] + dist_mat[indices[i][0]][costumer_pos[1]]) for i in range(hub_num)]
    index = dist.index(min(dist))
    route = [find_id(indices[index][0], points), costumer, costumer, find_id(indices[index][0], points)]
    rcost = route_cost(route, dist_mat, points, inv_points, data, fleet, )
    if find_id(indices[index][0], points) == 22:
        i = 0
    else:
        i = 1
    insert_values = (rcost, i, 'nr', 1, 2)
    return insert_values   

def Random_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat, indices, inv_points, fleet, veh_solution, pheromone_mat):
    random.shuffle(removed_req)
    insert_list = []
    for costumer in removed_req:     
        for i in range(hub_num):
            for route_ind, route in enumerate(partial_solution[i]):
                l = len(route)
                temp_route_p = route.copy()
                for j in range(1, l-1):
                    temp_route_p.insert(j, costumer)
                    # print('FEASIBILITY TEST: ', [len(partial_solution[0]),len(partial_solution[1])])
                    # print([len(veh_solution[0]),len(veh_solution[1])])
                    feasibility_d = feasibility_check(temp_route_p, points, inv_points, dist_mat, data, fleet, veh_solution[i][route_ind])
                    if feasibility_d:
                        for k in range(j+1, l):
                            temp_route_d = temp_route_p.copy()
                            temp_route_d.insert(k, costumer)
                            feasibility = feasibility_check(temp_route_d, points, inv_points, dist_mat, data, fleet, veh_solution[i][route_ind])
                            if feasibility:
                                insert_list.append((i, route_ind, j, k))
                            temp_route_d.pop(k)
                    temp_route_p.pop(j)
        if insert_list:
            insert = random.randint(0, len(insert_list)-1)
            i, route_ind, j, k = insert_list[insert]
            partial_solution[i][route_ind].insert(j, costumer)
            partial_solution[i][route_ind].insert(k, costumer)
        else:
            r, ind, veh_solution = create_route(costumer, dist_mat, indices, hub_num, points,  inv_points, fleet, veh_solution, pheromone_mat)
            partial_solution[ind].append(r)   
            #veh_solution[ind].append(2)
    return partial_solution, veh_solution

def Greedy_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat, indices, inv_points, chosen_ops, fleet, veh_solution, pheromone_mat):
    random.shuffle(removed_req)
    for costumer in removed_req:
        insert_list = []
        # Precalculate route costs and tardiness for each route
        route_costs = []
        #route_tardiness = []
        for i in range(hub_num):
            route_costs.append([])
            #route_tardiness.append([])
            for j in range(len(partial_solution[i])):                
                # print('ROUTE COST TEST: ', [len(partial_solution[0]),len(partial_solution[1])])
                # print([len(veh_solution[0]),len(veh_solution[1])])
                rcost = route_cost(partial_solution[i][j], dist_mat, points, inv_points, data, fleet, veh_solution[i][j])
                route_costs[i].append(rcost)
                # route_tardiness[i].append(total_tardiness)
        for i in range(hub_num):
            for route_ind, route in enumerate(partial_solution[i]):
                l = len(route)
                rcost = route_costs[i][route_ind]
                #total_tardiness = route_tardiness[i][route_ind]  
                temp_route_p = route.copy()
                for j in range(1, l-1):
                    temp_route_p.insert(j, costumer)
                    feasibility_d = feasibility_check(temp_route_p, points, inv_points, dist_mat, data, fleet, veh_solution[i][route_ind])
                    if feasibility_d:
                        for k in range(j+1, l):
                            temp_route_d = temp_route_p.copy()
                            temp_route_d.insert(k, costumer)
                            feasibility = feasibility_check(temp_route_d, points, inv_points, dist_mat, data, fleet, veh_solution[i][route_ind])
                            
                            if feasibility:
                                icost = insertion_cost(temp_route_d, rcost, dist_mat, points, inv_points, data, fleet, veh_solution, veh_solution[i][route_ind])
                                insert_list.append((icost, i, route_ind, j, k))
                            temp_route_d.pop(k)  
                    temp_route_p.pop(j)   
        if insert_list:
            min_cost, min_i, min_route_ind, min_j, min_k = heapq.nsmallest(1, insert_list, key=lambda x: x[0])[0]
            partial_solution[min_i][min_route_ind].insert(min_j, costumer)
            partial_solution[min_i][min_route_ind].insert(min_k, costumer)
        else:
            r, ind, veh_solution = create_route(costumer, dist_mat, indices, hub_num, points, inv_points, fleet, veh_solution, pheromone_mat)
            partial_solution[ind].append(r)
            #veh_solution[ind].append(2)
    return partial_solution, veh_solution

# def Greedy_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat, indices, inv_points, chosen_ops):
#     while removed_req:
#         costumer_insert_lists = deque()
#         greedy_values = deque()
#         # Precalculate route costs and tardiness for each route, for each request
#         route_costs = deque()
#         route_tardiness = deque()
#         for i in range(hub_num):
#             route_costs.append([])
#             route_tardiness.append([])
#             for route in partial_solution[i]:
#                 rcost, total_tardiness = route_cost(route, dist_mat, points, inv_points, data)
#                 route_costs[i].append(rcost)
#                 route_tardiness[i].append(total_tardiness)
#         for costumer in removed_req:
#             insert_list = deque([(1000000000,1,1,1,1)], maxlen=1)
#             for i in range(hub_num):
#                 for route_ind, route in enumerate(partial_solution[i]):
#                     rcost = route_costs[i][route_ind]
#                     total_tardiness = route_tardiness[i][route_ind]
                    
#                     temp_route_p = route.copy()
#                     feasibility_p = feasibility_check(temp_route_p, points, inv_points, dist_mat, data)
                    
#                     if feasibility_p:
#                         for j in range(1, len(route)-1):
#                             temp_route_p.insert(j, costumer)
#                             feasibility_d = feasibility_check(temp_route_p, points, inv_points, dist_mat, data)
                            
#                             if feasibility_d:
#                                 for k in range(j+1, len(route)):
#                                     temp_route_d = temp_route_p.copy()
#                                     temp_route_d.insert(k, costumer)
#                                     feasibility = feasibility_check(temp_route_d, points, inv_points, dist_mat, data)
                                    
#                                     if feasibility:
#                                         icost = insertion_cost(temp_route_d, rcost, dist_mat, points, inv_points, data)                                     # print(insert_list)
#                                         if icost < insert_list[0][0]:
#                                             insert_list.append((icost, i, route_ind, j, k))
                                        
#                                     # del temp_route_d[k]
#                             del temp_route_p[j]
#             costumer_insert_lists.append(insert_list)  
#             insert_values = new_route_insert_list(costumer, dist_mat, indices, hub_num, points, inv_points, data)
#             if insert_values[0] < insert_list[0][0]:
#                 insert_list.append(insert_values)   
                
#             if insert_list:
#                 # min_cost, min_i, min_route_ind, min_j, min_k = heapq.nsmallest(1, insert_list, key=lambda x: x[0])[0]
#                 min_cost, min_i, min_route_ind, min_j, min_k = insert_list[0]
#                 greedy_values.append((min_cost, min_i, min_route_ind, min_j, min_k, costumer))   
#         if greedy_values:
#             min_cost, min_i, min_route_ind, min_j, min_k, costumer = min(greedy_values, key=lambda x: x[0])
#             if min_route_ind == 'nr':
#                 r, ind = create_route(costumer, dist_mat, indices, hub_num, points, inv_points)
#                 partial_solution[ind].append(r)
#             else:
#                 partial_solution[min_i][min_route_ind].insert(min_j, costumer)
#                 partial_solution[min_i][min_route_ind].insert(min_k, costumer)
#             removed_req.remove(costumer)
#         else: #Failsafe 
#             r, ind = create_route(costumer, dist_mat, indices, hub_num, points,  inv_points)
#             partial_solution[ind].append(r)
            
#     return partial_solution

def Regret_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat, indices, inv_points, chosen_ops, regret, fleet, veh_solution):
    while removed_req:
        costumer_insert_lists = deque()
        regret_values = deque()
        
        # Precalculate route costs and tardiness for each route, for each request
        route_costs = deque()
        route_tardiness = deque()
        for i in range(hub_num):
            route_costs.append([])
            route_tardiness.append([])
            for route in partial_solution[i]:
                rcost, total_tardiness = route_cost(route, dist_mat, points, inv_points, data)
                route_costs[i].append(rcost)
                route_tardiness[i].append(total_tardiness) 
                
        for costumer in removed_req:
            insert_list = deque()

            for i in range(hub_num):
                for route_ind, route in enumerate(partial_solution[i]):
                    rcost = route_costs[i][route_ind]
                    total_tardiness = route_tardiness[i][route_ind]      
                    temp_route_p = route.copy()
                    feasibility_p = feasibility_check(temp_route_p, points, inv_points, dist_mat, data)     
                    if feasibility_p:
                        for j in range(1, len(route)-1):
                            temp_route_p.insert(j, costumer)
                            feasibility_d = feasibility_check(temp_route_p, points, inv_points, dist_mat, data)
                            
                            if feasibility_d:
                                for k in range(j+1, len(route)):
                                    temp_route_d = temp_route_p.copy()
                                    temp_route_d.insert(k, costumer)
                                    feasibility = feasibility_check(temp_route_d, points, inv_points, dist_mat, data)
                                    
                                    if feasibility:
                                        icost = insertion_cost(temp_route_d, rcost, dist_mat, points, inv_points, data)
                                        insert_list.append((icost, i, route_ind, j, k))                    
                                    temp_route_d.pop(k)                          
                            temp_route_p.pop(j) 
            
            insert_values = new_route_insert_list(costumer, dist_mat, indices, hub_num, points, inv_points, data)
            insert_list.append(insert_values)      
            costumer_insert_lists.append(insert_list)
            
            if insert_list:
                min_cost, min_i, min_route_ind, min_j, min_k = heapq.nsmallest(1, insert_list, key=lambda x: x[0])[0]
                sorted_array = sorted([arr for arr in insert_list if arr != (min_cost, min_i, min_route_ind, min_j, min_k)], key=lambda x: x[0])
                if sorted_array:
                    regret_values.append((sorted_array[regret][0] - min_cost, sorted_array[regret][1], sorted_array[regret][2], sorted_array[regret][3], sorted_array[regret][4], costumer))        

        if regret_values:
            sorted_array = sorted(regret_values, key=lambda x: x[0], reverse=True)
            # Choose the request with the highest regret value
            min_cost, min_i, min_route_ind, min_j, min_k, costumer = sorted_array[0]
            if min_route_ind == 'nr':
                r, ind = create_route(costumer, dist_mat, indices, hub_num, points, inv_points)
                partial_solution[ind].append(r)
            else:
                partial_solution[min_i][min_route_ind].insert(min_j, costumer)
                partial_solution[min_i][min_route_ind].insert(min_k, costumer)
            # regret_values.pop(0)
            removed_req.remove(costumer)
        else:
            #Failsafe if not enough (m) feasible insertions
            partial_solution = Greedy_Insertion(hub_num, [costumer], partial_solution, points, data, dist_mat, indices, inv_points, chosen_ops)
            removed_req.remove(costumer)
        
    return partial_solution, veh_solution

def RepairOperator(hub_num, removed_req, partial_solution, points, data, dist_mat, indices, inv_points, chosen_ops, fleet, veh_solution, pheromone_mat):
    if chosen_ops[1] == 'Greedy':
        solution, veh_solution = Greedy_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat, indices, inv_points, chosen_ops, fleet, veh_solution, pheromone_mat)
    elif chosen_ops[1] == 'Regret-2':
        regret = 0
        solution, veh_solution = Regret_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat, indices, inv_points, chosen_ops, regret, fleet, veh_solution, pheromone_mat)
    elif chosen_ops[1] == 'Regret-3':
        regret = 1
        solution, veh_solution = Regret_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat, indices, inv_points, chosen_ops, regret, fleet, veh_solution, pheromone_mat)
    elif chosen_ops[1] == 'Regret-4':
        regret = 2
        solution, veh_solution = Regret_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat, indices, inv_points, chosen_ops, regret, fleet, veh_solution, pheromone_mat)
    elif chosen_ops[1] == 'Random':
        solution, veh_solution = Random_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat, indices, inv_points, fleet, veh_solution, pheromone_mat)
    return solution, veh_solution