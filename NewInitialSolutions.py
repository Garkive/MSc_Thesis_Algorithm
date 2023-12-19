#Generate Initial Solutions with Greedy Insertion Function used in the ALNS

import pandas as pd
import csv
import DestroyOps
# import math
import heapq
import copy
import random
from collections import deque
import OperatorSelection

def import_data():
    indices = []
    with open('CSV_Files/Pickup_delivery_pairs2.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # convert each string to an integer
            row = [int(x) for x in row]
            indices.append(row)     
    routes = []
    with open('CSV_Files/Initial_solution.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # convert each string to an integer
            row = [int(x) for x in row]
            routes.append(row)
    hub_num = len(routes) #Number of depots
    dist_mat = []
    with open('CSV_Files/Distance_matrix2.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # convert each string to an integer
            row = [float(x) for x in row]
            dist_mat.append(row)
    filenames = ['CSV_Files/Pickup_delivery_info2.csv', 'CSV_Files/Processed_data2.csv']
    points = pd.read_csv(filenames[0])
    data = pd.read_csv(filenames[1])
    data = data.set_index('id')
    
    veh_types = pd.read_csv('CSV_Files/Vehicle_types.csv',sep = ';')
    veh_types.at[1,'id_transport_type'] = 2
    veh_types = veh_types.set_index('id_transport_type')
    
    return points, data, dist_mat, hub_num, routes, indices, veh_types

#Find costumer number from Pickup+Delivery id number
def find_pos(i_d,  inv_points):    
    pos = inv_points[i_d]
    return pos

#Find id number of a Pickup or Delivery
def find_id(pos, points):
    i_d = points['id'][pos]
    return i_d

#Change data structures for more efficient data accessing
def data_structures(points, data, hub_num, indices):
    
    points2 = points.to_dict()
    data2 = data.to_dict()
    indices2 = dict(enumerate(indices))
    
    inv_points2 = {}
    n = len(points['id']) - hub_num
    for index, row in points.iterrows():
        customer_id = row['id']
        pickup_number = int(index - n/2)
        delivery_number = index 
        if index <= hub_num:
            inv_points2[customer_id] = (delivery_number, 0)
        else:
            inv_points2[customer_id] = (pickup_number, delivery_number)
    return points2, data2, indices2, inv_points2

def gather_data(points, data, hub_num, indices, routes):
    points2, data2, indices2, inv_points2 = data_structures(points, data, hub_num, indices)
    
    solution = DestroyOps.display_routes(routes)
    id_list, solution_id = DestroyOps.solution_ids(solution, points, inv_points2)
    
    solution_id_copy = copy.deepcopy(id_list)
    return points2, data2, indices2, inv_points2, id_list, solution_id, solution_id_copy

def route_costNIS(route, dist_mat, points, inv_points, data, fleet): 
    auxiliary_list = []
    rcost = 0
    total_tardiness = 0
    time = 0
    
    veh_spd = fleet['speed'][2]
    service_time = 10 * 60
    
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
        
    return rcost, total_tardiness

#Calculates Cost of Inserting Request in Route
def insertion_costNIS(route, rcost, dist_mat, points, inv_points, data, fleet): 
    newrcost, total_tardiness = route_costNIS(route, dist_mat, points, inv_points, data, fleet)
    insertcost = newrcost - rcost
    return insertcost

# #Feasibility of Insertion 
def feasibility_checkNIS(route, points, inv_points, dist_mat, data, fleet):
    feasible = True
    current_weight = 0
    current_volume = 0
    current_time = 0
    
    weight_limit = fleet['max_weight'][2]
    volume_limit = fleet['capacity'][2]
    veh_spd = fleet['speed'][2]
    
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

def create_routeNIS(costumer, dist_mat, indices, hub_num, points, inv_points):
    costumer_pos = find_pos(costumer, inv_points)
    dist = [float(dist_mat[indices[i][0]][costumer_pos[0]] + dist_mat[indices[i][0]][costumer_pos[1]]) for i in range(hub_num)]
    index = dist.index(min(dist))
    route = [find_id(indices[index][0], points), costumer, costumer, find_id(indices[index][0], points)]
    return route, index

def new_route_insert_listNIS(costumer, dist_mat, indices, hub_num, points, inv_points, data, fleet):
    costumer_pos = find_pos(costumer, inv_points)
    dist = [float(dist_mat[indices[i][0]][costumer_pos[0]] + dist_mat[indices[i][0]][costumer_pos[1]]) for i in range(hub_num)]
    index = dist.index(min(dist))
    route = [find_id(indices[index][0], points), costumer, costumer, find_id(indices[index][0], points)]
    rcost, total_tardiness = route_costNIS(route, dist_mat, points, inv_points, data, fleet)
    if find_id(indices[index][0], points) == 22:
        i = 0
    else:
        i = 1
        
    insert_values = (rcost, i, 'nr', 1, 2)
    return insert_values  

def Regret_InsertionNIS(hub_num, removed_req, partial_solution, points2, data2, dist_mat, indices2, inv_points2, fleet):
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
                rcost, total_tardiness = route_costNIS(route, dist_mat, points2, inv_points2, data2, fleet)
                route_costs[i].append(rcost)
                route_tardiness[i].append(total_tardiness) 
        print('Removed Requests: ', removed_req)
        for costumer in removed_req:
            insert_list = deque()
            print('Costumer: ', costumer)
            for i in range(hub_num):
                for route_ind, route in enumerate(partial_solution[i]):
                    rcost = route_costs[i][route_ind]
                    total_tardiness = route_tardiness[i][route_ind]      
                    temp_route_p = route.copy()
                    feasibility_p = feasibility_checkNIS(temp_route_p, points2, inv_points2, dist_mat, data2, fleet)     
                    if feasibility_p:
                        for j in range(1, len(route)-1):
                            temp_route_p.insert(j, costumer)
                            feasibility_d = feasibility_checkNIS(temp_route_p, points2, inv_points2, dist_mat, data2, fleet)
                            
                            if feasibility_d:
                                for k in range(j+1, len(route)):
                                    temp_route_d = temp_route_p.copy()
                                    temp_route_d.insert(k, costumer)
                                    feasibility = feasibility_checkNIS(temp_route_d, points2, inv_points2, dist_mat, data2, fleet)
                                    
                                    if feasibility:
                                        icost = insertion_costNIS(temp_route_d, rcost, dist_mat, points2, inv_points2, data2, fleet)
                                        insert_list.append((icost, i, route_ind, j, k))                    
                                    temp_route_d.pop(k)                          
                            temp_route_p.pop(j) 
            
            insert_values = new_route_insert_listNIS(costumer, dist_mat, indices2, hub_num, points2, inv_points2, data2, fleet)
            insert_list.append(insert_values)      
            costumer_insert_lists.append(insert_list)
            if insert_list:
                min_cost, min_i, min_route_ind, min_j, min_k = heapq.nsmallest(1, insert_list, key=lambda x: x[0])[0]
                sorted_array = sorted([arr for arr in insert_list if arr != (min_cost, min_i, min_route_ind, min_j, min_k)], key=lambda x: x[0])
                if sorted_array:
                    regret_values.append((sorted_array[0][0] - min_cost, min_i, min_route_ind, min_j, min_k, costumer))        

        if regret_values:
            sorted_array = sorted(regret_values, key=lambda x: x[0], reverse=True)
            # Choose the request with the highest regret value
            min_cost, min_i, min_route_ind, min_j, min_k, costumer = sorted_array[0]
            if min_route_ind == 'nr':
                r, ind = create_routeNIS(costumer, dist_mat, indices2, hub_num, points2, inv_points2,fleet)
                partial_solution[ind].append(r)
            else:
                partial_solution[min_i][min_route_ind].insert(min_j, costumer)
                partial_solution[min_i][min_route_ind].insert(min_k, costumer)
            # regret_values.pop(0)
            removed_req.remove(costumer)
        else:
            #Failsafe if not enough (m) feasible insertions
            partial_solution = Greedy_InsertionNIS(hub_num, [costumer], partial_solution, points2, data2, dist_mat, indices2, inv_points2, fleet)
            removed_req.remove(costumer)
        
    return partial_solution


# def Greedy_Insertion(hub_num, removed_req, partial_solution, points2, data2, dist_mat, indices2, inv_points2):
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
#                 rcost, total_tardiness = route_cost(route, dist_mat, points2, inv_points2, data2, fleet)
#                 route_costs[i].append(rcost)
#                 route_tardiness[i].append(total_tardiness)
#         for costumer in removed_req:
#             insert_list = deque()
#             for i in range(hub_num):
#                 for route_ind, route in enumerate(partial_solution[i]):
#                     rcost = route_costs[i][route_ind]
#                     total_tardiness = route_tardiness[i][route_ind]
                    
#                     temp_route_p = deque(route.copy())
#                     feasibility_p = feasibility_check(temp_route_p, points2, inv_points2, dist_mat, data2, fleet)
                    
#                     if feasibility_p:
#                         for j in range(1, len(route)-1):
#                             temp_route_p.insert(j, costumer)
#                             feasibility_d = feasibility_check(temp_route_p, points2, inv_points2, dist_mat, data2, fleet)
                            
#                             if feasibility_d:
#                                 for k in range(j+1, len(route)):
#                                     temp_route_d = deque(temp_route_p.copy())
#                                     temp_route_d.insert(k, costumer)
#                                     feasibility = feasibility_check(temp_route_d, points2, inv_points2, dist_mat, data2, fleet)
                                    
#                                     if feasibility:
#                                         icost = insertion_cost(temp_route_d, rcost, dist_mat, points2, inv_points2, data2, fleet)
#                                         insert_list.append((icost, i, route_ind, j, k))
                                        
#                                     del temp_route_d[k]
                                    
#                             del temp_route_p[j]
#             costumer_insert_lists.append(insert_list)  
#             insert_values = new_route_insert_list(costumer, dist_mat, indices2, hub_num, points2, inv_points2, data2, fleet)
#             insert_list.append(insert_values)              
#             if insert_list:
#                 min_cost, min_i, min_route_ind, min_j, min_k = heapq.nsmallest(1, insert_list, key=lambda x: x[0])[0]
#                 greedy_values.append((min_cost, min_i, min_route_ind, min_j, min_k, costumer))
#         if greedy_values:
#             sorted_array = sorted(greedy_values, key=lambda x: x[0])
#             min_cost, min_i, min_route_ind, min_j, min_k, costumer = sorted_array[0]
#             if min_route_ind == 'nr':
#                 r, ind = create_route(costumer, dist_mat, indices2, hub_num, points2, inv_points2, fleet)
#                 partial_solution[ind].append(r)
#             else:
#                 partial_solution[min_i][min_route_ind].insert(min_j, costumer)
#                 partial_solution[min_i][min_route_ind].insert(min_k, costumer)
#             removed_req.remove(costumer)
#         else: #Failsafe 
#             r, ind = create_route(costumer, dist_mat, indices2, hub_num, points2, inv_points2, fleet)
#             partial_solution[ind].append(r)
            
#     return partial_solution

def Greedy_InsertionNIS(hub_num, removed_req, partial_solution, points2, data2, dist_mat, indices2, inv_points2, fleet, veh_solution, pheromone_mat):
    
    random.shuffle(removed_req)
    
    for costumer in removed_req:                            
        insert_list = []
        
        # Precalculate route costs and tardiness for each route
        route_costs = []
        route_tardiness = []
        for i in range(hub_num):
            route_costs.append([])
            route_tardiness.append([])
            for route in partial_solution[i]:
                rcost, total_tardiness = route_costNIS(route, dist_mat, points2, inv_points2, data2, fleet)
                route_costs[i].append(rcost)
                route_tardiness[i].append(total_tardiness)

        for i in range(hub_num):
            for route_ind, route in enumerate(partial_solution[i]):
                rcost = route_costs[i][route_ind]
                total_tardiness = route_tardiness[i][route_ind]
                
                temp_route_p = route.copy()
                feasibility_p = feasibility_checkNIS(temp_route_p, points2, inv_points2, dist_mat, data2, fleet)
                if feasibility_p:
                    for j in range(1, len(route)-1):
                        temp_route_p.insert(j, costumer)
                        feasibility_d = feasibility_checkNIS(temp_route_p, points2, inv_points2, dist_mat, data2, fleet)

                        if feasibility_d:
                            for k in range(j+1, len(route)):
                                temp_route_d = temp_route_p.copy()
                                temp_route_d.insert(k, costumer)
                                feasibility = feasibility_checkNIS(temp_route_d, points2, inv_points2, dist_mat, data2, fleet)
                                if feasibility:
                                    icost = insertion_costNIS(temp_route_d, rcost, dist_mat, points2, inv_points2, data2, fleet)
                                    insert_list.append((icost, i, route_ind, j, k))
                                temp_route_d.pop(k)      
                        temp_route_p.pop(j)       
        if insert_list:
            min_cost, min_i, min_route_ind, min_j, min_k = heapq.nsmallest(1, insert_list, key=lambda x: x[0])[0]
            partial_solution[min_i][min_route_ind].insert(min_j, costumer)
            partial_solution[min_i][min_route_ind].insert(min_k, costumer)
        else:
            r, ind = create_routeNIS(costumer, dist_mat, indices2, hub_num, points2,  inv_points2)
            partial_solution[ind].append(r)
            vehicle = OperatorSelection.vehicle_selection(r, fleet, pheromone_mat, points2, inv_points2)
            veh_solution[ind].append(vehicle)
    return partial_solution, veh_solution

def InitialSolution(points2, data2, indices2, inv_points2, hub_num, dist_mat, choice, fleet, veh_solution, pheromone_mat):
    partial_solution = [[] for _ in range(hub_num)]
    removed_req = list(data2['longitude_do'].keys())
    if choice == 1:
        solution, veh_solution = Greedy_InsertionNIS(hub_num, removed_req, partial_solution, points2, data2, dist_mat, indices2, inv_points2, fleet, veh_solution, pheromone_mat)
    elif choice == 2:
        solution, veh_solution = Regret_InsertionNIS(hub_num, removed_req, partial_solution, points2, data2, dist_mat, indices2, inv_points2, fleet, veh_solution, pheromone_mat)

    return solution, veh_solution
