#Adaptive Large Neighborhood Search (ALNS) algorithm with Simulated Annealing acceptance criteria
#to solve the VRPPD with multiple depots, time windows, capacitated (volume and weight).
#It deals with a specific case from a real world distribution company as well as the Li & Lim benchmarks.

#Modules DestroyOps.py and RepairOps.py contain the main heuristics as well as the required support
#functions. OperatorSelection.py contains all weight and score update functions as well as
#function to select heuristics. AcceptanceCriteria.py contains a simple Simulated Annealing 
#acceptance function.

#By: João Moura, MSc. in Mechanical Engineering @ Instituto Superior Técnico, Lisbon, 2023
import matplotlib.pyplot as plt
import DestroyOps
import RepairOps
import OperatorSelection
import AcceptanceCriteria
import PlotsAndResults
import NewInitialSolutions
import BenchmarkPreprocess
import time
import copy
import random
import csv

#Change current working directory
import os
#os.chdir('C:\\Users\\exemp\\Desktop\\Tese de Mestrado\\Código')
os.chdir('C:\\Users\\João Moura\\Documents\\GitHub\\MSc_Thesis_Algorithm')

#Decide which initial solution to use
initial_sol = 1 #1 for random Greedy Insertion, 2 for NN
choice = 1 #1 for Greedy Insertion, 2 for Regret-2

#Decide if company data or benchmark
choice2 = 0 #0 if company data, 1 if benchmark

#If benchmark, provide the file name
file = 'lc101.txt'
#file = 'LC1_2_1.txt'

max_iter = 1000
time_limit = 300000
weight_update_iter = 50
# weight_update_iter = 200 #Iteration interval for weight/score update/reset

iter_threshold = dict(enumerate([round(max_iter/6),round(max_iter/4),round(max_iter/4 *2),round(max_iter/4 *3), round(max_iter)]))

dest_heuristics = ['Shaw', 'Random']
rep_heuristics = ['Greedy', 'Regret-2', 'Regret-3', 'Regret-4', 'Random']

#Change data structures for more efficient data accessing
def data_structures(points, data, hub_num, indices, choice2):
    
    points2 = points.to_dict()
    data2 = data.to_dict()
    indices2 = dict(enumerate(indices))
    
    if choice2 == 0:
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
    else:
        return points2, data2, indices2
    
def gather_data(points, data, hub_num, indices, routes, choice2):
    if choice2 == 0:
        points2, data2, indices2, inv_points2 = data_structures(points, data, hub_num, indices, choice2)
    else:
        points2, data2, indices2 = data_structures(points, data, hub_num, indices, choice2)
        return points2, data2, indices2
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

def is_new_solution(previous_solutions,solution):
    for visited_solution in previous_solutions:
        if are_solutions_equal(solution, visited_solution):
            return False, previous_solutions
    
    previous_solutions.add(make_hashable(solution))
    return True, previous_solutions

def are_solutions_equal(solution1, solution2):
    if len(solution1) != len(solution2):
        return False
    for depot1, depot2 in zip(solution1, solution2):
        if len(depot1) != len(depot2):
            return False
        if not are_routes_equal(depot1, depot2):
            return False
    return True

def are_routes_equal(route1, route2):
    if len(route1) != len(route2):
        return False
    for i in range(len(route1)):
        if route1[i] != route2[i]:
            return False
    
    return True

aug_scores = dict(enumerate([80, 9, 13]))
#aug_scores = dict(enumerate([33, 9, 13])) #Score increasing parameters sigma 1,2 and 3
r = 0.1 #Reaction Factor - Controls how quickly weights are updated/changing
score_dest = [0]*2 #List that keeps track of scores for destroy operators
score_rep = [0]*5 #List that keeps track of scores for repair operators
w_dest = [1]*2 #First entry is Shaw, second is Random and third is Worst Removals
w_rep = [1,1,0,0,1] #First entry is Greedy Insertion, second is Regret-2
teta_dest = [0]*2 #List that keeps track of number of times destroy operator is used
teta_rep = [0]*5 #List that keeps track of number of times repair operator is used

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
    if chosen_ops[1] == 'Regret-2':
        teta_rep[1] += 1
    if chosen_ops[1] == 'Regret-3':
        teta_rep[2] += 1
    if chosen_ops[1] == 'Regret-4':
        teta_rep[3] += 1
    if chosen_ops[1] == 'Random':
        teta_rep[4] += 1
    return teta_dest, teta_rep

if choice2 == 0:
    points, data, dist_mat, hub_num, routes, indices = DestroyOps.import_data()
    points['service_time'] = [600]*(len(indices)*2-hub_num)
    points2, data2, indices2, inv_points2, id_list, solution_id, solution_id_copy = gather_data(points, data, hub_num, indices, routes, choice2)
elif choice2 == 1:
    points, data, dist_mat, hub_num, routes, indices = DestroyOps.import_data()
    points, data, indices, inv_points2, dist_mat, hub_num, solution_id_copy, veh_capacity, max_vehicles = BenchmarkPreprocess.import_and_process_data(file)
    points2, data2, indices2 = gather_data(points, data, hub_num, indices, routes, choice2)
chosen_ops = [0]*2

#Simulated Annealing Parameters
w = 0.35 #Starting Temperature parameter
# cooling_rate = 0.99994
cooling_rate = 0.9995
#cooling_rate = 0.99975

start_time = time.time()

#Acquire random Initial Solutions
init_sol = NewInitialSolutions.InitialSolution(points2, data2, indices2, inv_points2, hub_num, dist_mat, choice)

#Empty variables to display results
time_array = []
w_evolve = [] 
new_sol_cost_evolve = []
global_sol_cost_evolve = []
current_sol_cost_evolve = []

#Generic start variables
current_time = 0
current_iter = 1
gamma = 0.2 #Variable for degree of destruction

if initial_sol == 1:
    best_sol = init_sol
elif initial_sol == 2:
    best_sol = solution_id #MAYBE CHANGE??
    
best_sol_cost, initial_tardiness = RepairOps.solution_cost(best_sol, dist_mat, points, inv_points2, data)
print('Initial Solution Cost: ', best_sol_cost)
global_best = best_sol
global_best_cost = best_sol_cost
print('Initial Solution:', best_sol)
temperature = AcceptanceCriteria.calculate_starting_temperature(best_sol_cost, w)
print('Starting temp: ', temperature)
accept = False

#Iteration run time performance test variables
time_greedy = []
time_random = []
time_regret2 = []

perf_measure_greedy = []
perf_measure_random = []
perf_measure_regret2 = []
#ADAPTIVE LARGE NEIGHBOURHOOD SEARCH 
while current_iter <= max_iter and current_time < time_limit:
    
    time1 = time.time()
    accept_prob = 0
    
    print('Iteration:', current_iter, flush=True)
    score_case = [False]*3
    
    #Choose Heuristics for this iteration and increment teta values
    chosen_ops = OperatorSelection.Roulette_Selection(w_dest, w_rep, dest_heuristics, rep_heuristics, chosen_ops) 
    teta_dest, teta_rep = increment_teta(teta_dest, teta_rep, chosen_ops)
    
    #Destroy Solution
    partial_solution, removed_req = DestroyOps.DestroyOperator(
        solution_id_copy, best_sol, points2, inv_points2, data2, dist_mat, hub_num, indices2, chosen_ops, current_iter, iter_threshold, gamma
    )
    
    time2 = time.time()
    
    #Repair Solution
    current_sol = RepairOps.RepairOperator(
        hub_num, removed_req, partial_solution, points2, data2, dist_mat, indices2, inv_points2, chosen_ops
    )
        
    time3 = time.time()
    print('Repair: ', time3-time2)
    
    if chosen_ops[1] == 'Greedy':
        time_greedy.append(time3-time2)
    elif chosen_ops[1] == 'Random': 
        time_random.append(time3-time2)
    elif chosen_ops[1] == 'Regret-2': 
        time_regret2.append(time3-time2)
        
    #Calculate cost of obtained solution
    newsol_cost, total_tardiness = RepairOps.solution_cost(current_sol, dist_mat, points, inv_points2, data)
    
    
    #Acceptance Criteria
    accept_prob = AcceptanceCriteria.SimulatedAnnealing(newsol_cost, best_sol_cost, temperature, cooling_rate)
    
    if random.random() < accept_prob:
        accept = True
    else:
        accept = False    
    
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
    w_evolve.append((w_dest[0], w_dest[1], w_rep[0], w_rep[1], w_rep[2], w_rep[3], w_rep[4]))
    time_array.append(time.time()-start_time)
    
    #Update scores
    score_dest, score_rep = OperatorSelection.score_update(score_dest, score_rep, aug_scores, score_case, chosen_ops)        
    
    #Time and Iteration update
    current_time = time.time() - start_time
    current_iter += 1
    
    #Weight updates and score resets
    if current_iter % weight_update_iter == 0:
        
        perf_measure_greedy.append(score_rep[0]/sum(time_greedy))
        time_greedy = []
        perf_measure_random.append(score_rep[4]/sum(time_random))
        time_random = []
        perf_measure_regret2.append(score_rep[1]/sum(time_regret2))
        time_regret2 = []
        
        w_dest, w_rep = OperatorSelection.weights_update(score_dest, score_rep, w_dest, w_rep, teta_dest, teta_rep, aug_scores, r)
        score_dest = [0]*2 
        score_rep = [0]*5
        teta_dest = [0]*2 
        teta_rep = [0]*5
        

        
        
    #Temperature update
    temperature *= cooling_rate
    
iteration = current_iter - 1    

#Evaluate cost of final best solution, redundant, but just for additional checking
global_best_cost, total_tardiness = RepairOps.solution_cost(global_best, dist_mat, points, inv_points2, data)

print('Cost of final solution is:', global_best_cost)
# print('Total tardiness of solution is:', total_tardiness)
print('Total time:', current_time)

PlotsAndResults.SimpleWeightsPlot(iteration, w_evolve)
PlotsAndResults.WeightsFillPlot(max_iter, w_evolve)
PlotsAndResults.SolutionCostsPlot(iteration, new_sol_cost_evolve, global_sol_cost_evolve, current_sol_cost_evolve)

formatted_time = "{:.2f}".format(current_time)
formatted_cost = "{:.2f}".format(global_best_cost)

iterations_heurtimetest = [i for i in range(weight_update_iter, max_iter+1, weight_update_iter)]

plt.plot(iterations_heurtimetest, perf_measure_greedy, label='Greedy')
plt.plot(iterations_heurtimetest, perf_measure_random, label='Random')
plt.plot(iterations_heurtimetest, perf_measure_regret2, label='Regret-2')

# Adding labels and a legend
plt.xlabel('Iterations')
plt.ylabel('Performance Measure')
plt.legend()

# Displaying the plot
plt.show()

#Save Results
if choice2 == 0:
    name = f"CompanyData_{iteration}_{formatted_time}_{formatted_cost}.csv"
else:
    name = f"BenchmarkData_{iteration}_{formatted_time}_{formatted_cost}.csv"

results = []


for i in range(hub_num):
    resultwrite = {"Depot": i, "Route": global_best[i]}
    results.append(resultwrite)

header = ["Depot","Route"]
with open(name, mode="w", newline="") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=header)

    # Write the header row
    writer.writeheader()

    # Write the results
    for result in results:
        writer.writerow(result)

print(f"Results saved to {name}")