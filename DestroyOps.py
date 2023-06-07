#Destroy operators development to be used in the ALNS framework

#Input - Initial Solution
#Output - Destroyed Solution without some requests

#These requests will subsequently be submit to a repair operator where they will
#be reintroduced in the solution

#Operators initially considered:
    #1 - Shaw Removal or Related Removal
    #2 - Worst Removal
    #3 - Random Removal 
    #4 - Route Removal
    
#A parameter q will determine the "degree of destruction" desired, this may be 
#a fixed value or fluctuating, depending on the desired algorithm behaviour.

#Higher values promote diversity but may never converge to a good solution. 
#Lower values reduces diversification by reducing the search space.

#The value that q takes is between 0 and 1, representing the percentage of the 
#destroyed in each iteration.

import pandas as pd
import csv
import random
import copy

def import_data():
    
    indices = []
    with open('CSV_Files/Pickup_delivery_pairs.csv', 'r') as file:
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
    with open('CSV_Files/Distance_matrix.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            # convert each string to an integer
            row = [float(x) for x in row]
            dist_mat.append(row)
    
    filenames = ['CSV_Files/Pickup_delivery_info.csv', 'CSV_Files/Processed_data.csv']
    points = pd.read_csv(filenames[0])
    data = pd.read_csv(filenames[1])
    data = data.set_index('id')
    return points, data, dist_mat, hub_num, routes, indices

#Find costumer number from Pickup+Delivery id number
def find_pos(i_d,  inv_points):    
    pos = inv_points[i_d]
    return pos

#Find id number of a Pickup or Delivery
def find_id(pos, points):
    i_d = points['id'][pos]
    return i_d

#Organize solution in routes
def display_routes(routes): 
     solution = []
     for i in range(len(routes)):
         hub_sol = []
         route_sol = []
         start_route = True
         for j in range(len(routes[i])):
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
 
#Obtain the array of ids included in solution
def solution_ids(solution, points, inv_points):
    hub_ids = []
    id_list = []
    solution_id = copy.deepcopy(solution)
    for i in range(len(solution)):
        hub_ids.append(find_id(i, points))
        for j in range(len(solution[i])):
            for l in range(len(solution[i][j])):
                solution_id[i][j][l] = find_id(solution_id[i][j][l], points)
            id_nums = [find_id(x,points) for x in solution[i][j]]
            for k in range(len(id_nums)):
                
                if id_nums[k] not in id_list and id_nums[k] not in hub_ids:
                    id_list.append(id_nums[k])
    return id_list, solution_id

 
#Calculate relatedness measure between current customer and every other in the solution
def relatedness(j, L, dist_mat, data, phi, xi, qsi, inv_points):    
    relatedness = []
    for i in range(len(L)):
        p = L[i]
        p_2 = find_pos(p, inv_points)
        j_2 = find_pos(j, inv_points)
        relate = phi*(dist_mat[j_2[0]][p_2[0]]+dist_mat[j_2[1]][p_2[1]]) + xi*((data['start_time_pu'][j]-data['start_time_pu'][p])+(data['end_time_pu'][j]-data['end_time_pu'][p])) + qsi*(data['weight'][j]-data['weight'][p])
        relatedness.append(relate) 
    L_sort = [x for _, x in sorted(zip(relatedness, L))]
    return L_sort
    
#Update the solution to partial solution
def partial_sol(solution_id, D):
    partial_solution = []
    #print('Solution: ', solution_id)
    for i in range(len(solution_id)):
        temp_sol = []
        for j in range(len(solution_id[i])):
                g = [h for h in solution_id[i][j] if h not in D]
                temp_sol.append(g)
        partial_solution.append(temp_sol)
    return partial_solution    
        
#SHAW REMOVAL
def Shaw_removal(indices, hub_num, q, p, solution_id_copy, dist_mat, solution_id, points, inv_points, data, phi, xi, qsi):
    #Define a copy of the current solution 
    i = random.choice(solution_id_copy)
    D = [i]
    L = copy.deepcopy(solution_id_copy)
    L.remove(D)
    while len(D) < q:
        j = random.choice(list(D))
        #Temporary set with all current solution costumers not included in D
        #Compute relatedness metric between j and all elements in L, sort L according to it
        L_sort = relatedness(j, L, dist_mat, data, phi, xi, qsi, inv_points)
        E = round((random.random()**p)*(len(L)-1)) #Uniformly choose y in [0,1); E = y^p* len(L)
        #Select costumer L[E] from L and insert it into D
        D.append(L_sort[E])
        L.remove(L_sort[E])
    partial_solution = partial_sol(solution_id, D)
    #[find_id(x[0],points) for x in indices]
    partial_solution = remove_empty_routes(partial_solution, points)
    return partial_solution, D

#RANDOM REMOVAL
# def Worst_Removal(indices, ):
    
#     return partial_solution, D

#Remove empty routes from generated partial solution
def remove_empty_routes(partial_solution, points):
    for i in range(len(partial_solution)):
        empty = [find_id(i,points), find_id(i,points)]
        partial_solution[i] = [j for j in partial_solution[i] if j!=empty] 
    return partial_solution

def DestroyOperator(solution_id_copy, solution_id, points, inv_points, data, dist_mat, hub_num, routes, indices, chosen_ops, current_iter, iter_threshold):
    n, deg, p, phi, xi, qsi = variables(indices, hub_num)
    if current_iter < iter_threshold[0]:
        d = deg[0]
    elif current_iter < iter_threshold[1]:
        d = deg[1]
    elif current_iter < iter_threshold[2]:
        d = deg[2]
    elif current_iter < iter_threshold[3]:
        d = deg[3]
    elif current_iter < iter_threshold[4]:
        d = deg[4]
    else:
        d = deg[0]
    q = round(n*d) #Number of pairs to be removed each iteration
    
    if chosen_ops[0] == 'Random':
        p = 1
    partial_solution, removed_req = Shaw_removal(indices, hub_num, q, p, solution_id_copy, dist_mat, solution_id, points, inv_points, data, phi, xi, qsi)
    #print('Removed Requests: ', removed_req)
    return partial_solution, removed_req

def variables(indices, hub_num):
    n = len(indices)-hub_num #Number of pickup delivery pairs
    deg = [0.4, 0.3, 0.25, 0.2, 0.1] #Degree of destruction
    p = 20 #Introduces randomness in selection of requests
    phi = 5#Weight of distance in relatedness parameter
    xi = 3#Weight of time in relatedness parameter
    qsi = 2#Weight of demand in relatedness parameter
    return n, deg, p, phi, xi, qsi