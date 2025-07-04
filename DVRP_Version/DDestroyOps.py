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

import random
import copy

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
        
#RANDOM/SHAW REMOVAL
def Shaw_removal(indices, hub_num, q, p, solution_id_copy, dist_mat, solution_id, points, inv_points, data, phi, xi, qsi, veh_solution, fixed_req):
    print('Solution id copy: ',solution_id_copy)
    #CHANGE SOLUTION_ID_COPY TO NOT INCLUDE FIXED_REQS
    #Define a copy of the current solution 
    i = random.choice(solution_id_copy)

    D = [i]
    L = copy.deepcopy(solution_id_copy)
    L.remove(i)
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
    partial_solution, veh_solution = remove_empty_routes(partial_solution, points, veh_solution)
    return partial_solution, D, veh_solution

#ROUTE REMOVAL
def Route_removal(solution, veh_solution):
    unique = []
    removed_req = []
    route_choices = []
    for i in range(len(solution)):
        depot_choice = [(j-1,i) for j in range(1, len(solution[i])+1)]
        route_choices += depot_choice
    chosen_route = random.choice(route_choices)
    popped_route = solution[chosen_route[1]].pop(chosen_route[0])
    del veh_solution[chosen_route[1]][chosen_route[0]]
    for i in range(len(popped_route)):
        unique.append(popped_route[i])
    del unique[-1]
    del unique[0]
    [removed_req.append(x) for x in unique if x not in removed_req]
    return solution, removed_req, veh_solution

#Remove empty routes from generated partial solution
def remove_empty_routes(partial_solution, points, veh_solution):
    aux_list = []
    for i in range(len(partial_solution)):
        empty = [find_id(i,points), find_id(i,points)]
        for j in range(len(partial_solution[i])):
            if partial_solution[i][j] == empty:
                aux_list.append((i,j))
    for k in reversed(range(len(aux_list))): 
        del partial_solution[aux_list[k][0]][aux_list[k][1]]
        del veh_solution[aux_list[k][0]][aux_list[k][1]]
    return partial_solution, veh_solution

def DestroyOperator(solution_id_copy, solution_id, points, inv_points, data, dist_mat, hub_num, indices, chosen_ops, current_iter, gamma, veh_solution, fixed_req):
    n, p, phi, xi, qsi = variables(indices, hub_num)
    q = random.randint(4, round(n*gamma))
    #q = round(n*d) #Number of pairs to be removed each iteration   
    if chosen_ops[0] == 'Random':
        p = 1
        partial_solution, removed_req, veh_solution = Shaw_removal(indices, hub_num, q, p, solution_id_copy, dist_mat, solution_id, points, inv_points, data, phi, xi, qsi, veh_solution, fixed_req)
    if chosen_ops[0] == 'Shaw':
        partial_solution, removed_req, veh_solution = Shaw_removal(indices, hub_num, q, p, solution_id_copy, dist_mat, solution_id, points, inv_points, data, phi, xi, qsi, veh_solution, fixed_req)
    if chosen_ops[0] == 'Route Removal':
        partial_solution, removed_req, veh_solution = Route_removal(solution_id, veh_solution)
    return partial_solution, removed_req, veh_solution

def variables(indices, hub_num):
    n = len(indices)-hub_num #Number of pickup delivery pairs
    p = 6 #Introduces randomness in selection of requests
    phi = 5#Weight of distance in relatedness parameter
    xi = 3#Weight of time in relatedness parameter
    qsi = 2#Weight of demand in relatedness parameter
    return n, p, phi, xi, qsi