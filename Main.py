#Adaptive Large Neighborhood Search (ALNS) algorithm with Simulated Annealing acceptance criteria
#to solve the VRPPD with multiple depots, time windows, capacitated and with heterogenous fleet.
#It deals with a specific case from a real world distribution company as well as the Li & Lim benchmarks.

#Modules DestroyOps.py and RepairOps.py contain the main heuristics as well as the required support
#functions. OperatorSelection.py contains all weight and score update functions as well as
#function to select heuristics. AcceptanceCriteria.py contains a simple Simulated Annealing 
#acceptance function.

#By: João Moura, MSc. in Mechanical Engineering @ Instituto Superior Técnico, Lisbon, 2024

#Change current working directory
import os
# os.chdir('C:\\Users\\Utilizador\\Desktop\\CodigoMain')
os.chdir('C:\\Users\\João Moura\\Documents\\GitHub\\MSc_Thesis_Algorithm')

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
import numpy as np
from scipy.interpolate import make_interp_spline

# def main():

# os.chdir('C:\\Users\\exemp\\Desktop\\MSc_Thesis_Algorithm-main\\MSc_Thesis_Algorithm-main')
# os.chdir('C:\\Users\\1483498\\Desktop\\Python Extra\\MSc_Thesis_Algorithm-main')

#Decide if company data or benchmark
choice2 = 0 #0 if company data, 1 if benchmark
choice3 = 1 #0 if 20 costumers, 1 if 156 costumers
#If benchmark, provide the file name
file = 'lrc201.txt'
# file = 'LR1_2_1.txt'

#Generic start variables
current_time = 0
current_iter = 1
max_iter = 50000
time_limit = 100000
weight_update_iter = 100

iter_threshold = dict(enumerate([round(max_iter/6),round(max_iter/4),round(max_iter/4 *2),round(max_iter/4 *3), round(max_iter)]))

dest_heuristics = ['Shaw', 'Random', 'Route Removal']
rep_heuristics = ['Greedy', 'Regret-2', 'Regret-3', 'Regret-4', 'Random']
use_noise = [True, False]

#Change data structures for more efficient data accessing
def data_structures(points, data, hub_num, indices, veh_types, choice2):
    points2 = points.to_dict()
    data2 = data.to_dict()
    indices2 = dict(enumerate(indices))
    
    if choice2 == 0:
        fleet = veh_types.to_dict()
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
        return points2, data2, indices2, inv_points2, fleet
    else:
        return points2, data2, indices2
    
def gather_data(points, data, hub_num, indices, routes, veh_types, choice2):
    if choice2 == 0:
        points2, data2, indices2, inv_points2, fleet = data_structures(points, data, hub_num, indices, veh_types, choice2)
    else:
        points2, data2, indices2 = data_structures(points, data, hub_num, indices, [], choice2)
        return points2, data2, indices2
    solution = DestroyOps.display_routes(routes)
    id_list, solution_id = DestroyOps.solution_ids(solution, points, inv_points2)
    solution_id_copy = copy.deepcopy(id_list)
    return points2, data2, indices2, inv_points2, fleet, id_list, solution_id, solution_id_copy

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

#Increment teta values, that indicate how many times each heuristic was selected
def increment_teta(teta_dest, teta_rep, teta_noise, chosen_ops):
    #Noise
    if chosen_ops[2] == True:
        teta_noise[0] += 1
    if chosen_ops[2] == False:
        teta_noise[1] += 1
    #Destroy Ops
    if chosen_ops[0] == 'Shaw':
        teta_dest[0] += 1
    if chosen_ops[0] == 'Random':
        teta_dest[1] += 1
    if chosen_ops[0] == 'Route Removal':
        teta_dest[2] += 1
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
    return teta_dest, teta_rep, teta_noise

aug_scores = dict(enumerate([33, 9, 13])) #Score increasing parameters sigma 1,2 and 3
r = 0.1 #Reaction Factor - Controls how quickly weights are updated/changing
score_dest = [0]*3 #List that keeps track of scores for destroy operators
score_rep = [0]*5 #List that keeps track of scores for repair operators
score_noise = [0]*2 #List that keeps track of noise score
w_dest = [1]*3 #First entry is Shaw, second is Random and third is Route Removal
w_rep = [1,1,0,0,1] #First entry is Greedy Insertion, followed by Regret-2, Regret-3, Regret-4 and 
w_noise = [0,1] #First entry is Noise = True, second is Noise = False
teta_dest = [0]*3 #List that keeps track of number of times destroy operator is used
teta_rep = [0]*5 #List that keeps track of number of times repair operator is used
teta_noise = [0]*2 #List that keeps track of number of time noise is used
gamma = 0.2 #Variable for degree of destruction
n_factor = 0.025 #Variable for the noise factor

#SIMULATED ANNEALING PARAMETERS
w = 0.05 #Starting Temperature parameter
cooling_rate = 0.01**(1/max_iter) #So that Tfinal = 0.2% of Tstart

if choice2 == 0:
    points, data, dist_mat, hub_num, routes, indices, veh_types = NewInitialSolutions.import_data(choice3)
    points['service_time'] = [300]*(len(indices)*2-hub_num)
    points2, data2, indices2, inv_points2, fleet, id_list, solution_id, solution_id_copy = gather_data(points, data, hub_num, indices, routes, veh_types, choice2)
elif choice2 == 1:
    points, data, dist_mat, hub_num, routes, indices, veh_types = NewInitialSolutions.import_data(choice3)
    points, data, indices, inv_points2, dist_mat, hub_num, solution_id_copy, veh_types = BenchmarkPreprocess.import_and_process_data(file)
    fleet = veh_types.to_dict()
    points2, data2, indices2 = gather_data(points, data, hub_num, indices, routes, [], choice2)

# Initialize empty variables
chosen_ops = [0]*3
veh_sol = []
for i in range(hub_num):
    veh_sol.append([])
 
#Starting Time
start_time = time.time()
# Pheromone variables
delta_rho = 0.2
evap = 0.001

def Initiate_pheromone(data, fleet, indices, hub_num, delta_rho, evap, points, choice2):
    # #Pheromone matrix structure
    n_veh = len(fleet['description'])
    n_points = (len(indices)-hub_num)*2+hub_num
    if choice2 == 0:
        pheromone_mat = [[[0 for _ in range(n_points)] for _ in range(n_points)] for _ in range(n_veh)]
        for i in range(1,n_veh+1):
            for j in range(n_points): 
                for k in range(hub_num, n_points):
                    pheromone_mat[i-1][j][k] =  data['weight'][RepairOps.find_id(k, points)]/fleet['max_weight'][i] + data['volume'][RepairOps.find_id(k, points)]/fleet['capacity'][i]  
        # Set diagonal elements to 0
        for matrix in pheromone_mat:
            for i in range(n_points):
                matrix[i][i] = 0
        return np.array(pheromone_mat)
    elif choice2 == 1:
        pheromone_mat = [[[1 for _ in range(n_points)] for _ in range(n_points)] for _ in range(n_veh)]
        # Set diagonal elements to 0
        for matrix in pheromone_mat:
            for i in range(n_points):
                matrix[i][i] = 0
        return np.array(pheromone_mat)

pheromone_mat = Initiate_pheromone(data, fleet, indices, hub_num, delta_rho, evap, points, choice2)

#Relatedness normalization values
pu_norm = max(list(data['start_time_pu']))-min(list(data['start_time_pu']))
do_norm = max(list(data['start_time_do']))-min(list(data['start_time_do']))
load_norm = abs(max(list(data['weight']), key=abs))-abs(min(list(data['weight']), key=abs))

#NOISE COMPUTATION
max_dist = max(dist for dist_array in dist_mat for dist in dist_array) #Maximum distance between nodes
max_veh_cost = max_cost = max(fleet['cost_km'][vehicle] for vehicle in list(fleet['cost_km'].keys())) #Maximum vehicle cost
max_N = n_factor*(max_dist*max_cost) #Noise interval threshold

#Acquire random Initial Solutions
init_sol, init_veh = NewInitialSolutions.InitialSolution(points2, data2, indices2, inv_points2, hub_num, dist_mat, fleet, veh_sol, pheromone_mat)

#Empty variables to display results and metrics
time_array = []
w_evolve = [] 
new_sol_cost_evolve = []
global_sol_cost_evolve = []
current_sol_cost_evolve = []
time_greedy = []
time_random = []
time_regret2 = []
time_regret3 = []
perf_measure_greedy = []
perf_measure_random = []
perf_measure_regret2 = []
perf_measure_regret3 = []

best_sol = init_sol
best_sol_cost = RepairOps.solution_cost(best_sol, dist_mat, points, inv_points2, data, fleet, veh_sol)
print('Initial Solution Cost: ', best_sol_cost)
global_best = copy.deepcopy(best_sol)
global_best_cost = copy.deepcopy(best_sol_cost)
best_veh_sol = copy.deepcopy(init_veh)
global_best_veh = copy.deepcopy(init_veh)
print('Initial Solution:', best_sol)
temperature = AcceptanceCriteria.calculate_starting_temperature(best_sol_cost, w)
print('Starting temp: ', temperature)
accept = False

def ALNS_destroy_repair(solution_id_copy, best_sol, points2, inv_points2, data2, dist_mat, hub_num, indices2, chosen_ops, current_iter, iter_threshold, gamma, best_veh_sol, pheromone_mat, max_N, pu_norm, do_norm, max_dist, load_norm):
    #Destroy Solution
    partial_solution, removed_req, partial_veh_solution = DestroyOps.DestroyOperator(
        solution_id_copy, best_sol, points2, inv_points2, data2, dist_mat, hub_num, indices2, chosen_ops, current_iter, iter_threshold, gamma, best_veh_sol, pu_norm, do_norm, max_dist, load_norm
    )
    #Repair Solution
    current_sol, current_veh_sol = RepairOps.RepairOperator(
        hub_num, removed_req, partial_solution, points2, data2, dist_mat, indices2, inv_points2, chosen_ops, fleet, partial_veh_solution, pheromone_mat, max_N
    )
    return current_sol, current_veh_sol

def verify_feas(solution, points, inv_points2, dist_mat, data2, fleet, vehicles):
    feas = []
    for i in range(len(solution[0])):
        route = solution[0][i]
        feasible = RepairOps.feasibility_check(route, points, inv_points2, dist_mat, data2, fleet, vehicles[0][i])
        feas.append(feasible)
    if False in feas:
        return False
    else: 
        return True

#ADAPTIVE LARGE NEIGHBOURHOOD SEARCH 
while current_iter <= max_iter and current_time < time_limit:

    accept_prob = 0
    
    print('Iteration: ', current_iter)
    
    score_case = [False]*3

    #Choose Heuristics for this iteration and increment teta values
    chosen_ops = OperatorSelection.Roulette_Selection(w_dest, w_rep, w_noise, dest_heuristics, rep_heuristics, use_noise, chosen_ops) 
    teta_dest, teta_rep, teta_noise = increment_teta(teta_dest, teta_rep, teta_noise, chosen_ops)
    
    time2 = time.time()
    
    best_sol_copy = copy.deepcopy(best_sol)
    best_veh_sol_copy = copy.deepcopy(best_veh_sol)

    #DESTROY/REPAIR PROCEDURE
    current_sol, current_veh_sol = ALNS_destroy_repair(solution_id_copy, best_sol_copy, points2, inv_points2, data2, dist_mat, hub_num, indices2, chosen_ops, current_iter, iter_threshold, gamma, best_veh_sol_copy, pheromone_mat, max_N, pu_norm, do_norm, max_dist, load_norm)
    
    # feas = verify_feas(current_sol, points, inv_points2, dist_mat, data2, fleet, current_veh_sol)
    # if feas == False:
    #     print('Infeasible solution found.')
    #     print(current_sol)
    #     print(current_veh_sol)
    #     break

    time3 = time.time()
    # print('Repair: ', time3-time2)
    
    if chosen_ops[1] == 'Greedy':
        time_greedy.append(time3-time2)
    elif chosen_ops[1] == 'Random': 
        time_random.append(time3-time2)
    elif chosen_ops[1] == 'Regret-2': 
        time_regret2.append(time3-time2)
    elif chosen_ops[1] == 'Regret-3': 
        time_regret3.append(time3-time2)
       
    #Calculate cost of obtained solution
    newsol_cost = RepairOps.solution_cost(current_sol, dist_mat, points, inv_points2, data, fleet, current_veh_sol)
    
    if newsol_cost < best_sol_cost:
        pheromone_mat = OperatorSelection.Pheromones_update(pheromone_mat, best_sol, 'Local', delta_rho, inv_points2)
    #Acceptance Criteria
    accept_prob = AcceptanceCriteria.SimulatedAnnealing(newsol_cost, best_sol_cost, temperature, cooling_rate)
    
    if random.random() < accept_prob:
        accept = True
    else:
        accept = False    

    if accept:
        # print('Accepted.')
        is_new, previous_solutions = is_new_solution(previous_solutions, current_sol)    
        if newsol_cost < global_best_cost:
            score_case[0] = True
            global_best_cost = copy.deepcopy(newsol_cost)
            global_best = copy.deepcopy(current_sol)
            global_best_veh = copy.deepcopy(current_veh_sol)
            pheromone_mat = OperatorSelection.Pheromones_update(pheromone_mat, best_sol, 'Global', delta_rho, inv_points2)
            print('Solution Improved - Cost:', global_best_cost, flush=True)
            print('Solution Improved - Vehicles:', len(global_best_veh[0]), flush=True)
            # print('Solution Tardiness:', total_tardiness, flush=True)
           
        elif is_new and newsol_cost < best_sol_cost:
            score_case[1] = True    
        elif is_new and newsol_cost > best_sol_cost:
            score_case[2] = True
        
        best_veh_sol = copy.deepcopy(current_veh_sol)
        best_sol = copy.deepcopy(current_sol)
        best_sol_cost = copy.deepcopy(newsol_cost)
        
    
    
    #Update cost and weight arrays for results
    new_sol_cost_evolve.append(newsol_cost)
    current_sol_cost_evolve.append(best_sol_cost)
    global_sol_cost_evolve.append(global_best_cost)
    w_evolve.append((w_dest[0], w_dest[1], w_dest[2], w_rep[0], w_rep[1], w_rep[2], w_rep[3], w_rep[4]))
    time_array.append(time.time()-start_time)
    
    #Update scores
    score_dest, score_rep, score_noise = OperatorSelection.score_update(score_dest, score_rep, score_noise, aug_scores, score_case, chosen_ops)        
    
    #Time and Iteration update
    current_time = time.time() - start_time
    current_iter += 1
    
    #Weight updates and score resets
    if current_iter % weight_update_iter == 0:
        if sum(time_greedy) == 0:
            perf_measure_greedy.append(0)
        else:
            perf_measure_greedy.append(score_rep[0]/sum(time_greedy))
        if sum(time_random) == 0:
            perf_measure_random.append(0)
        else:
            perf_measure_random.append(score_rep[4]/sum(time_random))
        if sum(time_regret2) == 0:
            perf_measure_regret2.append(0)
        else:
            perf_measure_regret2.append(score_rep[1]/sum(time_regret2))
        if sum(time_regret3) == 0:
            perf_measure_regret3.append(0)
        else:
            perf_measure_regret3.append(score_rep[2]/sum(time_regret3))
        time_greedy = []
        time_random = []
        time_regret2 = []
        time_regret3 = []
        
        w_dest, w_rep, w_noise = OperatorSelection.weights_update(score_dest, score_rep, score_noise, w_dest, w_rep, w_noise, teta_dest, teta_rep, teta_noise, aug_scores, r)
        score_dest = [0]*3
        score_rep = [0]*5
        score_noise = [0]*2
        teta_dest = [0]*3
        teta_rep = [0]*5
        teta_noise = [0]*2
        

        
        
    #Temperature and Pheromone update
    temperature *= cooling_rate
    pheromone_mat = pheromone_mat*(1-evap)

    
print('Global best: ', global_best)
print(global_best_veh)
iteration = current_iter - 1    

#Evaluate cost of final best solution, redundant, but just for additional checking
global_best_cost = RepairOps.solution_cost(global_best, dist_mat, points, inv_points2, data, fleet, global_best_veh)

print('Cost of final solution is:', global_best_cost)
# print('Total tardiness of solution is:', total_tardiness)
print('Total time:', current_time)

PlotsAndResults.SimpleWeightsPlot(iteration, w_evolve)
PlotsAndResults.WeightsFillPlot(max_iter, w_evolve)
PlotsAndResults.SolutionCostsPlot(iteration, new_sol_cost_evolve, global_sol_cost_evolve, current_sol_cost_evolve)

formatted_time = "{:.2f}".format(current_time)
formatted_cost = "{:.2f}".format(global_best_cost)


#------------- PERFORMANCE MEASURE PLOT ---------------
iterations_heurtimetest = np.array([i for i in range(weight_update_iter, max_iter+1, weight_update_iter)])
iterations_heurtimetest = np.mean(iterations_heurtimetest.reshape(-1,int((2*max_iter)/2000)), axis=1)
perf_measure_greedy = np.array(perf_measure_greedy)
perf_measure_greedy = np.mean(perf_measure_greedy.reshape(-1,int((2*max_iter)/2000)), axis=1)
perf_measure_random = np.array(perf_measure_random)
perf_measure_random = np.mean(perf_measure_random.reshape(-1,int((2*max_iter)/2000)), axis=1)
perf_measure_regret2 = np.array(perf_measure_regret2)
perf_measure_regret2= np.mean(perf_measure_regret2.reshape(-1,int((2*max_iter)/2000)), axis=1)
perf_measure_regret3 = np.array(perf_measure_regret3)
perf_measure_regret3= np.mean(perf_measure_regret3.reshape(-1,int((2*max_iter)/2000)), axis=1)

X_Y1_Spline = make_interp_spline(iterations_heurtimetest, perf_measure_greedy)
X_Y2_Spline = make_interp_spline(iterations_heurtimetest, perf_measure_random)
X_Y3_Spline = make_interp_spline(iterations_heurtimetest, perf_measure_regret2)
X_Y4_Spline = make_interp_spline(iterations_heurtimetest, perf_measure_regret3)

X_ = np.linspace(iterations_heurtimetest.min(), iterations_heurtimetest.max(), 500)

Y1_ = X_Y1_Spline(X_)
Y2_ = X_Y2_Spline(X_)
Y3_ = X_Y3_Spline(X_)
Y4_ = X_Y4_Spline(X_)

plt.plot(X_, Y1_, label='Greedy')
plt.plot(X_, Y2_, label='Random')
plt.plot(X_, Y3_, label='Regret2')
plt.plot(X_, Y4_, label='Regret3')
# plt.plot(iterations_heurtimetest, perf_measure_regret2, label='Regret-2')

# Adding labels and a legend
plt.title('Heuristic Performance Measure')
plt.xlabel('Iterations')
plt.ylabel('Performance Measure')
plt.legend()
plt.grid()
# Displaying the plot
plt.show()
#------------------------------------------------------

#Save Results
if choice2 == 0:
    name = f"CompanyData_{iteration}_{formatted_time}_{formatted_cost}.csv"
else:
    no_veh = len(global_best_veh[0])
    name = f"BenchmarkData_{file}_{iteration}_{formatted_time}_{formatted_cost}_{no_veh}.csv"

results = []


for i in range(hub_num):
    resultwrite = {"Depot": i, "Route": global_best[i], "Vehicle": global_best_veh[i]}
    results.append(resultwrite)

header = ["Depot","Route","Vehicle"]
with open(name, mode="w", newline="") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=header)

    # Write the header row
    writer.writeheader()

    # Write the results
    for result in results:
        writer.writerow(result)

print(f"Results saved to {name}")

# if __name__ == "__main__":
#     main()