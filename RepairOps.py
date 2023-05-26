import time
import pandas as pd

#Find costumer number from Pickup+Delivery id number
def find_pos(i_d, points):    
    
    pos = [i for i,x in enumerate(points['id']) if x==i_d]    
    return pos
#Find id number of a Pickup or Delivery
def find_id(pos, points):
    
    i_d = points.iloc[pos]['id']
    return i_d

def route_cost(route, dist_mat, points, data): 
    auxiliary_list = []
    rcost = 0
    total_tardiness = 0
    time = 0

    for i in range(len(route)-1):
        p1 = find_pos(route[i], points)[auxiliary_list.count(route[i])]
        auxiliary_list.append(route[i])

        if i+1 != len(route)-1:
            p2 = find_pos(route[i+1], points)[auxiliary_list.count(route[i+1])]
            e_time = 'end_time_do'
            s_time = 'start_time_do'
        else:
            p2 = find_pos(route[i+1], points)[0]
            e_time = 'end_time_pu'
            s_time = 'start_time_pu'

        travel_time = dist_mat[p1][p2] / 15
        arrival_time = time + travel_time + 600

        if i+1 != len(route)-1 and arrival_time > data[e_time].loc[find_id(p2, points)]:
            tardiness = max(arrival_time - data[e_time].loc[find_id(p2, points)], 0)
            total_tardiness += tardiness
            time = max(arrival_time, data[s_time].loc[find_id(p2, points)] + 600)
        else:
            time = arrival_time
            tardiness = 0

        rcost += dist_mat[p1][p2] + tardiness
        
    return rcost, total_tardiness

#Calculates Total Solution Cost (Using route_cost function)
def solution_cost(solution, dist_mat, points, data):
    scost = 0
    sol_tardiness = 0
    for hub_routes in solution:
        for route in hub_routes:
            rcost, total_tardiness = route_cost(route,dist_mat, points, data)
            scost += rcost
            sol_tardiness += total_tardiness
    return scost, sol_tardiness

#Calculates Cost of Inserting Request in Route
def insertion_cost(route, rcost, dist_mat, points, data): 
    newrcost, total_tardiness = route_cost(route, dist_mat, points, data)
    insertcost = newrcost - rcost
    return insertcost

#Feasibility of Insertion 
def feasibility_check(route, points, dist_mat, data):
    feasible = True
    auxiliary_list = []  # List to keep track of pickup or delivery
    current_weight = 0
    current_volume = 0
    current_time = 0

    weight_limit = 30
    volume_limit = 3000000
    service_time = 10 * 60
    veh_spd = 15

    for i in range(1, len(route) - 1):
        if i != len(route) - 1:
            weight = data['weight'][route[i]]
            volume = data['volume'][route[i]]
            
            if current_weight + weight > weight_limit or current_volume + volume > volume_limit:
                feasible = False
                break
            
            current_weight += weight
            current_volume += volume

        if route[i-1] in auxiliary_list and i-1 != 0:
            p1 = find_pos(route[i-1], points)[1]
        else:
            p1 = find_pos(route[i-1], points)[0]
            auxiliary_list.append(route[i-1])

        if route[i] in auxiliary_list and i != len(route) - 1:
            p2 = find_pos(route[i], points)[1]
            s_time = 'start_time_do'
        else:
            s_time = 'start_time_pu'
            p2 = find_pos(route[i], points)[0]

        travel_time = dist_mat[p1][p2] / veh_spd
        arrival_time = data[s_time].loc[find_id(p2, points)]

        if current_time + travel_time > arrival_time:
            current_time += travel_time + service_time
        else:
            current_time = arrival_time + service_time

    return feasible



def create_route(customer, dist_mat, indices, hub_num, points):
    customer_pos = find_pos(customer, points)
    dist = [float(dist_mat[indices[i][0]][customer_pos[0]] + dist_mat[indices[i][0]][customer_pos[1]]) for i in range(hub_num)]
    index = dist.index(min(dist))
    route = [find_id(indices[index][0], points), customer, customer, find_id(indices[index][0], points)]
    return route, index

#Greedy Insertion Repair Operator   
# def Greedy_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat, indices):
    
#     for costumer in removed_req:
#         insert_list = []
#         cost_list = []
#         for i in range(hub_num):
#             for route_ind, route in enumerate(partial_solution[i]):
#                 rcost, total_tardiness = route_cost(route, dist_mat, points, data)
#                 temp_route_p = route.copy()  
#                 for j in range(1, len(route)-1):
#                     temp_route_p.insert(j, costumer)
#                     is_feasible = feasibility_check(temp_route_p, points, dist_mat, data)
#                     if is_feasible == False:
#                         temp_route_p.pop(j)  
#                         continue
#                     for k in range(j+1, len(route)):
#                         temp_route_d = temp_route_p.copy()  
#                         temp_route_d.insert(k, costumer)
#                         is_feasible = feasibility_check(temp_route_d, points, dist_mat, data)
#                         if is_feasible == False:
#                             temp_route_d.pop(k)  
#                             continue
#                         icost = insertion_cost(temp_route_d, rcost, dist_mat, points, data)
#                         insert_index = [i, route_ind, j, k]
#                         insert_list.append(insert_index)
#                         cost_list.append(icost)
#                         temp_route_d.pop(k)  
#                     temp_route_p.pop(j)  
                
#         if len(cost_list) != 0:
#             index = cost_list.index(min(cost_list))
#             i, route_ind, j, k = insert_list[index]
#             partial_solution[i][route_ind].insert(j, costumer)
#             partial_solution[i][route_ind].insert(k, costumer)
#         else:
#             r, ind = create_route(costumer, dist_mat, indices, hub_num, points)
#             partial_solution[ind].append(r)
            
#     return partial_solution
import heapq

def Greedy_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat, indices):
    for customer in removed_req:
        insert_list = []
        
        # Precalculate route costs and tardiness for each route
        route_costs = []
        route_tardiness = []
        for i in range(hub_num):
            route_costs.append([])
            route_tardiness.append([])
            for route in partial_solution[i]:
                rcost, total_tardiness = route_cost(route, dist_mat, points, data)
                route_costs[i].append(rcost)
                route_tardiness[i].append(total_tardiness)

        for i in range(hub_num):
            for route_ind, route in enumerate(partial_solution[i]):
                rcost = route_costs[i][route_ind]
                total_tardiness = route_tardiness[i][route_ind]
                
                temp_route_p = route.copy()
                feasibility_p = feasibility_check(temp_route_p, points, dist_mat, data)
                
                if feasibility_p:
                    for j in range(1, len(route)-1):
                        temp_route_p.insert(j, customer)
                        feasibility_d = feasibility_check(temp_route_p, points, dist_mat, data)
                        
                        if feasibility_d:
                            for k in range(j+1, len(route)):
                                temp_route_d = temp_route_p.copy()
                                temp_route_d.insert(k, customer)
                                feasibility = feasibility_check(temp_route_d, points, dist_mat, data)
                                
                                if feasibility:
                                    icost = insertion_cost(temp_route_d, rcost, dist_mat, points, data)
                                    insert_list.append((icost, i, route_ind, j, k))
                                    
                                temp_route_d.pop(k)
                                
                        temp_route_p.pop(j)
                
        if insert_list:
            min_cost, min_i, min_route_ind, min_j, min_k = heapq.nsmallest(1, insert_list, key=lambda x: x[0])[0]
            partial_solution[min_i][min_route_ind].insert(min_j, customer)
            partial_solution[min_i][min_route_ind].insert(min_k, customer)
        else:
            r, ind = create_route(customer, dist_mat, indices, hub_num, points)
            partial_solution[ind].append(r)
            
    return partial_solution


# def RepairOperator():
#   newsol = Greedy_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat)
#   return
#solution = Greedy_Insertion(hub_num, removed_req, partial_solution, points, data, dist_mat)