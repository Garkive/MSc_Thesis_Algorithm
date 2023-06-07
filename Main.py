#Adaptive Large Neighborhood Search (ALNS) algorithm with Simulated Annealing acceptance criteria
#to solve the VRPPD with multiple depots, time windows, capacitated (volume and weight).
#So far it deals only with a specific case from a distribution company. Future work will
#include the Li & Lim Benchmarks from 2001 and capacity to deal with an heterogenous fleet.

#Modules DestroyOps.py and RepairOps.py contain the main heuristics as well as the required support
#functions. OperatorSelection.py contains all weight and score update functions as well as
#function to select heuristics. AcceptanceCriteria.py contains a simple Simulated Annealing 
#acceptance function.

#By: João Moura, MSc. @ Instituto Superior Técnico, Lisbon, 2023

import DestroyOps
import RepairOps
import OperatorSelection
import AcceptanceCriteria
import PlotsAndResults
import NewInitialSolutions
import time
import copy
import random

#Change current working directory
import os
os.chdir('C:\\Users\\exemp\\Desktop\\Tese de Mestrado\\Código')

#Decide which initial solution to use
initial_sol = 1 #1 for random Greedy Insertion, 2 for NN

max_iter = 1000
time_limit = 30000

iter_threshold = dict(enumerate([round(max_iter/6),round(max_iter/4),round(max_iter/4 *2),round(max_iter/4 *3), round(max_iter)]))

dest_heuristics = ['Shaw', 'Random']
rep_heuristics = ['Greedy', 'Regret']

points, data, dist_mat, hub_num, routes, indices = DestroyOps.import_data()

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

previous_solutions = set()

def make_hashable(obj):
    if isinstance(obj, list):
        return tuple(make_hashable(item) for item in obj)
    elif isinstance(obj, dict):
        return frozenset((make_hashable(k), make_hashable(v)) for k, v in obj.items())
    else:
        return obj

def is_new_solution(previous_solutions, solution):
    hashable_solution = make_hashable(solution)
    
    if hashable_solution in previous_solutions:
        return False, previous_solutions
    else:
        previous_solutions.add(hashable_solution)  # Add the hashable solution to the set
        return True, previous_solutions
    

#aug_scores = dict(enumerate([15, 4, 6]))
aug_scores = dict(enumerate([33, 9, 13])) #Score increasing parameters sigma 1,2 and 3
r = 0.1 #Reaction Factor - Controls how quickly weights are updated/changing
score_dest = [0]*2 #List that keeps track of scores for destroy operators
score_rep = [0]*2 #List that keeps track of scores for repair operators
w_dest = [2]*2 #First entry is Shaw, second is Random and third is Worst Removals
w_rep = [2]*2 #First entry is Greedy Insertion, second is Regret-2
teta_dest = [0]*2 #List that keeps track of number of times destroy operator is used
teta_rep = [0]*2 #List that keeps track of number of times repair operator is used



#Increment teta values, that indicate how many times each heuristic was selected
def increment_teta(teta_dest, teta_rep, chosen_ops):
    #Destroy Ops
    if chosen_ops[0] == 'Shaw':
        teta_dest[0] += 1
    if chosen_ops[0] == 'Random':
        teta_dest[1] += 1
    #Repair Ops    
    if chosen_ops[1] == 'Greedy':
        teta_rep[0] += 1
    if chosen_ops[1] == 'Regret':
        teta_rep[1] += 1
    return teta_dest, teta_rep
points2, data2, indices2, inv_points2, id_list, solution_id, solution_id_copy = gather_data(points, data, hub_num, indices, routes)

chosen_ops = [0]*2

#Simulated Annealing Parameters
w = 0.35 #Starting Temperature parameter
cooling_rate = 0.9997
#cooling_rate = 0.99975

start_time = time.time()

#Acquire random Initial Solutions
init_sol = NewInitialSolutions.InitialSolution(points2, data2, indices2, inv_points2, hub_num, dist_mat)

#Empty variables to display results
w_evolve = [] 
new_sol_cost_evolve = []
global_sol_cost_evolve = []
current_sol_cost_evolve = []

#Generic start variables
current_time = 0
current_iter = 1

if initial_sol == 1:
    best_sol = init_sol
elif initial_sol == 2:
    best_sol = solution_id
    
best_sol_cost, initial_tardiness = RepairOps.solution_cost(best_sol, dist_mat, points, inv_points2, data)
print('Initial Solution Cost: ', best_sol_cost)
global_best = best_sol
global_best_cost = best_sol_cost

temperature = AcceptanceCriteria.calculate_starting_temperature(best_sol_cost, w)

print('Starting temp: ', temperature)

accept = False

#Adaptive Large Neighborhood Search 
while current_iter <= max_iter and current_time < time_limit:
    
    accept_prob = 0
    
    print('Iteration:', current_iter, flush=True)
    
    score_case = [False]*3
    
    #Choose Heuristics for this iteration and increment teta values
    chosen_ops = OperatorSelection.Roulette_Selection(w_dest, w_rep, dest_heuristics, rep_heuristics, chosen_ops)    
    teta_dest, teta_rep = increment_teta(teta_dest, teta_rep, chosen_ops)
    
    #Destroy Solution
    partial_solution, removed_req = DestroyOps.DestroyOperator(
        solution_id_copy, best_sol, points2, inv_points2, data2, dist_mat, hub_num, routes, indices2, chosen_ops, current_iter, iter_threshold
    )
    
    #Repair Solution
    current_sol = RepairOps.RepairOperator(
        hub_num, removed_req, partial_solution, points2, data2, dist_mat, indices2, inv_points2, chosen_ops
    )

    #Calculate cost of obtained solution
    newsol_cost, total_tardiness = RepairOps.solution_cost(current_sol, dist_mat, points, inv_points2, data)
    
    #Acceptance Criteria
    accept_prob = AcceptanceCriteria.SimulatedAnnealing(newsol_cost, global_best_cost, temperature, cooling_rate)
    if random.random() < accept_prob:
        accept = True
    else:
        accept = False    
    
    #Conditional Solution updates and scores
    if accept:
        is_new, previous_solutions = is_new_solution(previous_solutions, current_sol)
        
        
        if newsol_cost < global_best_cost:
            score_case[0] = True
            global_best_cost = newsol_cost
            global_best = current_sol
            print('Solution Improved - Cost:', global_best_cost, flush=True)
            print('Solution Tardiness:', total_tardiness, flush=True)
           
        elif is_new and newsol_cost < best_sol_cost:
            score_case[1] = True    
        elif is_new and newsol_cost > best_sol_cost:
            score_case[2] = True
        
        best_sol = current_sol
        best_sol_cost = newsol_cost
    
    #Update cost and weight arrays for results
    new_sol_cost_evolve.append(newsol_cost)
    current_sol_cost_evolve.append(best_sol_cost)
    global_sol_cost_evolve.append(global_best_cost)
    w_evolve.append((w_dest[0], w_dest[1], w_rep[0], w_rep[1]))
    
    #Update scores
    score_dest, score_rep = OperatorSelection.score_update(score_dest, score_rep, aug_scores, score_case, chosen_ops)        
    
    #Time and Iteration update
    current_time = time.time() - start_time
    current_iter += 1
    
    #Weight updates and score resets
    if current_iter % 50 == 0:
        
        print('Times each dest heuristic was chosen: ',teta_dest)
        print('Times each rep heuristic was chosen: ',teta_rep)
        
        w_dest, w_rep = OperatorSelection.weights_update(score_dest, score_rep, w_dest, w_rep, teta_dest, teta_rep, aug_scores, r)
        score_dest = [0]*2 
        score_rep = [0]*2 
        teta_dest = [0]*2 
        teta_rep = [0]*2 
        
    #Temperature update
    temperature *= cooling_rate
 
#Evaluate cost of final best solution, redundant, but just for additional checking
global_best_cost, total_tardiness = RepairOps.solution_cost(global_best, dist_mat, points, inv_points2, data)

print('Cost of final solution is:', global_best_cost)
print('Total tardiness of solution is:', total_tardiness)
print('Total time:', current_time)

PlotsAndResults.SimpleWeightsPlot(max_iter, w_evolve)
PlotsAndResults.SolutionCostsPlot(max_iter, new_sol_cost_evolve, global_sol_cost_evolve, current_sol_cost_evolve)