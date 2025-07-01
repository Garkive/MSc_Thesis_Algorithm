#Adaptive Large Neighborhood Search (ALNS) algorithm with Simulated Annealing acceptance criteria
#to solve the VRPPD with multiple depots, time windows, capacitated (volume and weight) and with heterogenous fleet.
#It deals with a specific case from a real world distribution company as well as the Li & Lim benchmarks.

#Modules DestroyOps.py and RepairOps.py contain the main heuristics as well as the required support
#functions. OperatorSelection.py contains all weight and score update functions as well as
#function to select heuristics. AcceptanceCriteria.py contains a simple Simulated Annealing 
#acceptance function.

#By: João Moura, MSc. in Mechanical Engineering @ Instituto Superior Técnico, Lisbon, 2024

import os
cwd = os.getcwd()
os.chdir(cwd)

import DDestroyOps
import DRepairOps
import DOperatorSelection
import DAcceptanceCriteria
import DPlotsAndResults
import DNewInitialSolutions
import DBenchmarkPreprocess
import DAuxiliaryFunctions
import DDynamicFunctions
import time
import copy
import random
import csv

#Decide if company data or benchmark
choice2 = 0 #0 if company data, 1 if benchmark
choice3 = 0 #0 if 20 costumers, 1 if 156 costumers

#If benchmark, provide the file name
# file = 'lr101.txt'
file = 'LC1_2_1.txt'

#Dynamic Variables
tstatic = 120 #Static solver time
treal = 2000 #Simulation real time factor
dod = 0.5 #Degree of dynamism
beta = 20*60 #Reaction Time after a request is received
time_window = 30*60 #Incremented time window variable for the 10 minutes of real-time simulation thresholds
new_req = [] #New request list

#Generic start variables
current_time = 0
current_iter = 1
max_iter = 5
time_limit = 45
weight_update_iter = 200

dest_heuristics = ['Shaw', 'Random', 'Route Removal']
rep_heuristics = ['Greedy', 'Regret-2', 'Regret-3', 'Regret-4', 'Random']

previous_solutions = set()

#Increment teta values, that indicate how many times each heuristic was selected
def increment_teta(teta_dest, teta_rep, chosen_ops):
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
    return teta_dest, teta_rep

aug_scores = dict(enumerate([33, 9, 13])) #Score increasing parameters sigma 1,2 and 3
r = 0.1 #Reaction Factor - Controls how quickly weights are updated/changing
score_dest = [0]*3 #List that keeps track of scores for destroy operators
score_rep = [0]*5 #List that keeps track of scores for repair operators
w_dest = [1]*3 #First entry is Shaw, second is Random and third is Route Removal
w_rep = [1,1,1,0,1] #First entry is Greedy Insertion, followed by Regret-2, Regret-3, Regret-4 and Random
teta_dest = [0]*3 #List that keeps track of number of times destroy operator is used
teta_rep = [0]*5 #List that keeps track of number of times repair operator is used
gamma = 0.2 #Variable for degree of destruction

#SIMULATED ANNEALING PARAMETERS
w = 0.1 #Starting Temperature parameter
cooling_rate = 0.002**(1/max_iter) #So that Tfinal = 0.2% of Tstart

if choice2 == 0:
    points, data, dist_mat, hub_num, routes, indices, veh_types = DNewInitialSolutions.import_data(choice3)
    points['service_time'] = [300]*(len(indices)*2-hub_num)
    points2, data2, indices2, inv_points2, fleet, id_list, solution_id, solution_id_copy = DAuxiliaryFunctions.gather_data(points, data, hub_num, indices, routes, veh_types, choice2)
elif choice2 == 1:
    points, data, dist_mat, hub_num, routes, indices, veh_types = DNewInitialSolutions.import_data(choice3)
    points, data, indices, inv_points2, dist_mat, hub_num, solution_id_copy, veh_types = DBenchmarkPreprocess.import_and_process_data(file)
    fleet = veh_types.to_dict()
    points2, data2, indices2 = DAuxiliaryFunctions.gather_data(points, data, hub_num, indices, routes, [], choice2)

# Initialize empty variables
chosen_ops = [0]*2
veh_sol = []
for i in range(hub_num):
    veh_sol.append([])
 
#Starting Time
start_time = time.time()

#Acquire dynamic request list
dyn_req = DDynamicFunctions.DynamicRequests(data, dod)

#Acquire dynamic request release times
release_time = DDynamicFunctions.ComputeReleaseTime(data, dod, fleet, dist_mat, beta, points, inv_points2, hub_num)

#Create list of requests excluding dynamic requests
solution_ids = list(data2['longitude_do'].keys())
solution_ids = [i for i in solution_ids if i not in dyn_req]

#Acquire random Initial Solutions
init_sol, init_veh = DNewInitialSolutions.InitialSolution(points2, data2, indices2, inv_points2, hub_num, dist_mat, fleet, veh_sol, solution_ids)

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
# best_sol_cost = DRepairOps.solution_cost(best_sol, dist_mat, points, inv_points2, data, fleet, veh_sol)
best_sol_cost = 10**10
print('Initial Solution Cost: ', best_sol_cost)
global_best = copy.deepcopy(best_sol)
global_best_cost = copy.deepcopy(best_sol_cost)
best_veh_sol = copy.deepcopy(init_veh)
global_best_veh = copy.deepcopy(init_veh)
print('Initial Solution:', best_sol)
temperature = DAcceptanceCriteria.calculate_starting_temperature(best_sol_cost, w)
print('Starting temp: ', temperature)
accept = False

def ALNS_destroy_repair(solution_id_copy, best_sol, points2, inv_points2, data2, dist_mat, hub_num, indices2, chosen_ops, current_iter, gamma, best_veh_sol, new_req, current_pos, fixed_req):
    # print('Before Destroy: ', best_sol)
    #Destroy Solution
    partial_solution, removed_req, partial_veh_solution = DDestroyOps.DestroyOperator(
        solution_id_copy, best_sol, points2, inv_points2, data2, dist_mat, hub_num, indices2, chosen_ops, current_iter, gamma, best_veh_sol, fixed_req
    )
    # print('Partial Solution: ',partial_solution)
    # print('Vehicle Solution: ',partial_veh_solution)
    # print('Removed Requests: ',removed_req)
    # print('New Requests: ',new_req)
    
    #Repair Solution
    current_sol, current_veh_sol = DRepairOps.RepairOperator(
        hub_num, removed_req, partial_solution, points2, data2, dist_mat, indices2, inv_points2, chosen_ops, fleet, partial_veh_solution
    )
    # print('Repaired Solution: ', current_sol)
    return current_sol, current_veh_sol



#ADAPTIVE LARGE NEIGHBOURHOOD SEARCH 
while current_iter <= max_iter and current_time < time_limit:
    new_req = []
    
    #Calculate Current Positions and Fixed Requests
    current_pos = DDynamicFunctions.CurrentPositionSolution(best_sol, points, inv_points2, dist_mat, data, fleet, best_veh_sol, current_time, treal)
    fixed_req = DDynamicFunctions.FixedRequests(current_pos, best_sol)
    
    if current_time*treal >= time_window: #Verify if the next threshold is met
        time_window += 600 #Increment time window
        #Check if new requests are to be inserted
        for dynamic_release in release_time:
            if current_time*treal > dynamic_release[1]:
                new_req.append(dynamic_release[0])
                release_time.remove(dynamic_release)
        print('New Requests: ', new_req)
        if new_req != []:
            solution_ids = solution_ids + new_req
        best_sol_cost = 10**10
    accept_prob = 0
    
    print('Iteration: ', current_iter)
    
    score_case = [False]*3

    #Choose Heuristics for this iteration and increment teta values
    chosen_ops = DOperatorSelection.Roulette_Selection(w_dest, w_rep, dest_heuristics, rep_heuristics, chosen_ops) 
    teta_dest, teta_rep = DOperatorSelection.increment_teta(teta_dest, teta_rep, chosen_ops)
    
    time2 = time.time()
    
    best_sol_copy = copy.deepcopy(best_sol)
    best_veh_sol_copy = copy.deepcopy(best_veh_sol)

    #DESTROY/REPAIR PROCEDURE
    current_sol, current_veh_sol = ALNS_destroy_repair(solution_ids, best_sol_copy, points2, inv_points2, data2, dist_mat, hub_num, indices2, chosen_ops, current_iter, gamma, best_veh_sol_copy, new_req, current_pos, fixed_req)
    
    # feas = DAuxiliaryFunctions.verify_feas(current_sol, points, inv_points2, dist_mat, data2, fleet, current_veh_sol)
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
    newsol_cost = DRepairOps.solution_cost(current_sol, dist_mat, points, inv_points2, data, fleet, current_veh_sol)
    
    #Acceptance Criteria
    accept_prob = DAcceptanceCriteria.SimulatedAnnealing(newsol_cost, best_sol_cost, temperature, cooling_rate)
    
    if random.random() < accept_prob:
        accept = True
    else:
        accept = False    

    if accept:
        is_new, previous_solutions = DAuxiliaryFunctions.is_new_solution(previous_solutions, current_sol)    
        if newsol_cost < global_best_cost:
            score_case[0] = True
            global_best_cost = copy.deepcopy(newsol_cost)
            global_best = copy.deepcopy(current_sol)
            global_best_veh = copy.deepcopy(current_veh_sol)
            print('Solution Improved - Cost:', global_best_cost, flush=True)
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
    score_dest, score_rep = DOperatorSelection.score_update(score_dest, score_rep, aug_scores, score_case, chosen_ops)        
    
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
        w_dest, w_rep = DOperatorSelection.weights_update(score_dest, score_rep, w_dest, w_rep, teta_dest, teta_rep, aug_scores, r)
        score_dest = [0]*3
        score_rep = [0]*5
        teta_dest = [0]*3
        teta_rep = [0]*5
    #Temperature update
    temperature *= cooling_rate

    
print('Global best: ', global_best)
print(global_best_veh)
iteration = current_iter - 1    

#Evaluate cost of final best solution, redundant, but just for additional checking
global_best_cost = DRepairOps.solution_cost(global_best, dist_mat, points, inv_points2, data, fleet, global_best_veh)

print('Cost of final solution is:', global_best_cost)
# print('Total tardiness of solution is:', total_tardiness)
print('Total time:', current_time)

DPlotsAndResults.SimpleWeightsPlot(iteration, w_evolve)
DPlotsAndResults.WeightsFillPlot(max_iter, w_evolve)
DPlotsAndResults.SolutionCostsPlot(iteration, new_sol_cost_evolve, global_sol_cost_evolve, current_sol_cost_evolve)

formatted_time = "{:.2f}".format(current_time)
formatted_cost = "{:.2f}".format(global_best_cost)


#------------- PERFORMANCE MEASURE PLOT ---------------
DPlotsAndResults.PerformanceMeasure(max_iter, weight_update_iter, perf_measure_greedy, perf_measure_random, perf_measure_regret2, perf_measure_regret3)
#------------------------------------------------------

#Save Results
if choice2 == 0:
    name = f"CompanyData_{iteration}_{formatted_time}_{formatted_cost}.csv"
else:
    name = f"BenchmarkData_{iteration}_{formatted_time}_{formatted_cost}.csv"

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