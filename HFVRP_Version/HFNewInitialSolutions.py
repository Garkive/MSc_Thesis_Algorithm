#Generate Initial Solutions with Greedy Insertion Function used in the ALNS

import pandas as pd
import csv
import HFDestroyOps
# import math
import heapq
import copy
import random
from collections import deque
import HFOperatorSelection

def import_data(choice):
    if choice == 0:
        pdpair = 'CSV_Files/Pickup_delivery_pairs.csv'
        pdinfo = 'CSV_Files/Pickup_delivery_info.csv'
        dmat = 'CSV_Files/Distance_matrix.csv'
        dat = 'CSV_Files/Processed_data.csv'
    elif choice == 1:
        pdpair = 'CSV_Files/Pickup_delivery_pairs2.csv'
        pdinfo = 'CSV_Files/Pickup_delivery_info2.csv'
        dmat = 'CSV_Files/Distance_matrix2.csv'
        dat = 'CSV_Files/Processed_data2.csv'
        
    indices = []
    with open(pdpair, 'r') as file:
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
    with open(dmat, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # convert each string to an integer
            row = [float(x) for x in row]
            dist_mat.append(row)
    filenames = [pdinfo, dat]
    print(filenames)
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
    
    solution = HFDestroyOps.display_routes(routes)
    id_list, solution_id = HFDestroyOps.solution_ids(solution, points, inv_points2)
    
    solution_id_copy = copy.deepcopy(id_list)
    return points2, data2, indices2, inv_points2, id_list, solution_id, solution_id_copy

def route_costNIS(route, dist_mat, points, inv_points, data, fleet, vehicle): 
    auxiliary_list = []
    rcost = 0
    total_tardiness = 0
    time = 0
    
    veh_spd = fleet['speed'][vehicle]
    service_time = 0
    
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
    
    rcost = rcost*fleet['variable_cost'][vehicle] + fleet['fixed_cost'][vehicle]
    # rcost = rcost*fleet['variable_cost'][vehicle]
    
    return rcost

#Calculates Cost of Inserting Request in Route
def insertion_costNIS(route, rcost, dist_mat, points, inv_points, data, fleet, veh_solution, vehicle): 
    newrcost = route_costNIS(route, dist_mat, points, inv_points, data, fleet, vehicle)
    insertcost = newrcost - rcost
    return insertcost

# #Feasibility of Insertion 
def feasibility_checkNIS(route, points, inv_points, dist_mat, data, fleet, vehicle):
    weight_limit = fleet['max_weight'][vehicle]
    weightsum = 0
    for i in range(len(route)):
        if route[i] != 0:
            weightsum += data['weight'][route[i]]
    if weightsum > weight_limit:
        return False
    else:
        return True

def create_routeNIS(costumer, dist_mat, indices, hub_num, points, data, inv_points, fleet, veh_solution, pheromone_mat, max_vol):
    costumer_pos = find_pos(costumer, inv_points)
    dist = [float(dist_mat[indices[i][0]][costumer_pos[0]] + dist_mat[indices[i][0]][costumer_pos[1]]) for i in range(hub_num)]
    index = dist.index(min(dist))
    route = [find_id(indices[index][0], points), costumer, find_id(indices[index][0], points)]
    vehicles = []
    for i in range(1,len(fleet['max_weight'])+1):
        feasible = feasibility_checkNIS(route, points, inv_points, dist_mat, data, fleet, i)
        if feasible:
            vehicles.append(i)
    choice_v = HFOperatorSelection.vehicle_selection(route, pheromone_mat, inv_points, vehicles)
    veh_solution[index].append(choice_v)
    return route, index, veh_solution

def new_route_insert_listNIS(costumer, dist_mat, indices, hub_num, points, inv_points, data, fleet):
    costumer_pos = find_pos(costumer, inv_points)
    dist = [float(dist_mat[indices[i][0]][costumer_pos[0]] + dist_mat[indices[i][0]][costumer_pos[1]]) for i in range(hub_num)]
    index = dist.index(min(dist))
    route = [find_id(indices[index][0], points), costumer, find_id(indices[index][0], points)]
    rcost, total_tardiness = route_costNIS(route, dist_mat, points, inv_points, data, fleet)
    if find_id(indices[index][0], points) == 22:
        i = 0
    else:
        i = 1   
    insert_values = (rcost, i, 'nr', 1, 2)
    return insert_values  

def Greedy_InsertionNIS(hub_num, removed_req, partial_solution, points2, data2, dist_mat, indices2, inv_points2, fleet, veh_solution, pheromone_mat):  
    random.shuffle(removed_req) 
    for costumer in removed_req:                            
        insert_list = []  
        # Precalculate route costs and tardiness for each route
        route_costs = []
        for i in range(hub_num):
            route_costs.append([])
            for j in range(len(partial_solution[i])):    
                rcost = route_costNIS(partial_solution[i][j], dist_mat, points2, inv_points2, data2, fleet, veh_solution[i][j])
                route_costs[i].append(rcost)
        for i in range(hub_num):
            for route_ind, route in enumerate(partial_solution[i]):
                l = len(route)
                rcost = route_costs[i][route_ind] 
                temp_route_p = route.copy()
                for j in range(1, l-1):
                    temp_route_p.insert(j, costumer)
                    feasibility_d = feasibility_checkNIS(temp_route_p, points2, inv_points2, dist_mat, data2, fleet, veh_solution[i][route_ind])
                    if feasibility_d:
                        icost = insertion_costNIS(temp_route_p, rcost, dist_mat, points2, inv_points2, data2, fleet, veh_solution, veh_solution[i][route_ind])
                        insert_list.append((icost, i, route_ind, j))
                    temp_route_p.pop(j)       
        if insert_list:
            min_cost, min_i, min_route_ind, min_j = heapq.nsmallest(1, insert_list, key=lambda x: x[0])[0]
            partial_solution[min_i][min_route_ind].insert(min_j, costumer)
        else:
            max_vol = data2['weight'][costumer]
            r, ind, veh_solution = create_routeNIS(costumer, dist_mat, indices2, hub_num, points2, data2, inv_points2, fleet, veh_solution, pheromone_mat, max_vol)
            partial_solution[ind].append(r)
    return partial_solution, veh_solution

def InitialSolution(points2, data2, indices2, inv_points2, hub_num, dist_mat, choice, fleet, veh_solution, pheromone_mat):
    partial_solution = [[] for _ in range(hub_num)]
    removed_req = list(data2['longitude_do'].keys())
    if choice == 1:
        solution, veh_solution = Greedy_InsertionNIS(hub_num, removed_req, partial_solution, points2, data2, dist_mat, indices2, inv_points2, fleet, veh_solution, pheromone_mat)

    return solution, veh_solution
