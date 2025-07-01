#Operator Selection Module for both destroy and repair operators

#To do:
#Define the weight system and functions that update the weights according to 
#success or failure of certain operators.
#Define a selection scheme for each operator in each iteration.

import random
import RepairOps

#Roulette Selection for destroy and repair heuristics
def Roulette_Selection(w_dest, w_rep, w_noise, dest_heuristics, rep_heuristics, use_noise, chosen_ops):
    chosen_ops[0] = random.choices(dest_heuristics, weights=w_dest, k=1)[0]
    chosen_ops[1] = random.choices(rep_heuristics, weights=w_rep, k=1)[0]
    chosen_ops[2] = random.choices(use_noise, weights=w_noise, k=1)[0]
    return chosen_ops

#Weights update
def weights_update(score_dest, score_rep, score_noise, w_dest, w_rep, w_noise, teta_dest, teta_rep, teta_noise, aug_scores, r):
    for i in range(len(w_dest)):
        if teta_dest[i] != 0:  # Check for division by zero
            w_dest[i] = w_dest[i] * (1 - r) + r * (score_dest[i] / teta_dest[i])
    for i in range(len(w_rep)):
        if teta_rep[i] != 0:  # Check for division by zero
            w_rep[i] = w_rep[i] * (1 - r) + r * (score_rep[i] / teta_rep[i])
    for i in range(len(w_noise)):
        if teta_noise[i] != 0:  # Check for division by zero
            w_noise[i] = w_noise[i] * (1 - r) + r * (score_noise[i] / teta_noise[i])
    return w_dest, w_rep, w_noise

#Score update when a solution is accepted
def score_update(score_dest, score_rep, score_noise, aug_scores, score_case, chosen_ops):
    if True in score_case:
        if chosen_ops[2] == True:
            if score_case[0] == True:
                score_noise[0] += aug_scores[0]
            elif score_case[1] == True:
                score_noise[0] += aug_scores[1]
            elif score_case[2] == True:
                score_noise[0] += aug_scores[2]
        if chosen_ops[2] == False:
            if score_case[0] == True:
                score_noise[1] += aug_scores[0]
            elif score_case[1] == True:
                score_noise[1] += aug_scores[1]
            elif score_case[2] == True:
                score_noise[1] += aug_scores[2]
        if chosen_ops[0] == 'Shaw':
            if score_case[0] == True:
                score_dest[0] += aug_scores[0]
            elif score_case[1] == True:
                score_dest[0] += aug_scores[1]
            elif score_case[2] == True:
                score_dest[0] += aug_scores[2]
        if chosen_ops[0] == 'Random':
            if score_case[0] == True:
                score_dest[1] += aug_scores[0]
            elif score_case[1] == True:
                score_dest[1] += aug_scores[1]
            elif score_case[2] == True:
                score_dest[1] += aug_scores[2]
        if chosen_ops[0] == 'Route Removal':
            if score_case[0] == True:
                score_dest[2] += aug_scores[0]
            elif score_case[1] == True:
                score_dest[2] += aug_scores[1]
            elif score_case[2] == True:
                score_dest[2] += aug_scores[2]
        if chosen_ops[1] == 'Greedy':
            if score_case[0] == True:
                score_rep[0] += aug_scores[0]
            elif score_case[1] == True:
                score_rep[0] += aug_scores[1]
            elif score_case[2] == True:
                score_rep[0] += aug_scores[2]     
        if chosen_ops[1] == 'Regret-2':
            if score_case[0] == True:
                score_rep[1] += aug_scores[0]
            elif score_case[1] == True:
                score_rep[1] += aug_scores[1]
            elif score_case[2] == True:
                score_rep[1] += aug_scores[2]  
        if chosen_ops[1] == 'Regret-3':
            if score_case[0] == True:
                score_rep[2] += aug_scores[0]
            elif score_case[1] == True:
                score_rep[2] += aug_scores[1]
            elif score_case[2] == True:
                score_rep[2] += aug_scores[2]  
        if chosen_ops[1] == 'Regret-4':
            if score_case[0] == True:
                score_rep[3] += aug_scores[0]
            elif score_case[1] == True:
                score_rep[3] += aug_scores[1]
            elif score_case[2] == True:
                score_rep[3] += aug_scores[2]  
        if chosen_ops[1] == 'Random':
            if score_case[0] == True:
                score_rep[4] += aug_scores[0]
            elif score_case[1] == True:
                score_rep[4] += aug_scores[1]
            elif score_case[2] == True:
                score_rep[4] += aug_scores[2] 
    return score_dest, score_rep, score_noise

def vehicle_selection(route, pheromone_mat, inv_points, vehicles):
    # arcs = Route_arcs(route, inv_points)
    # weights = []
    # for j in range(len(pheromone_mat)):
    #     weight = 0
    #     for i in range(len(arcs)):
    #         weight += pheromone_mat[j][arcs[i][0]][arcs[i][1]]
    #     weights.append(weight)
    # vehicle = random.choices(range(len(weights)), weights = weights, k = 1)[0] + 1
    vehicle = random.choices(vehicles,weights = [1 for v in vehicles], k = 1)[0]
    return vehicle

def Route_arcs(route, inv_points): 
    arcs = []
    auxiliary_list = []
    for i in range(len(route)-1):
        p1 = RepairOps.find_pos(route[i], inv_points)[auxiliary_list.count(route[i])]
        auxiliary_list.append(route[i])    
        if i+1 != len(route)-1:
            p2 = RepairOps.find_pos(route[i+1], inv_points)[auxiliary_list.count(route[i+1])]
        else:
            p2 = RepairOps.find_pos(route[i+1], inv_points)[0]
        arcs.append([p1, p2])
    return arcs

def Pheromones_update(pheromone_mat, solution, update, delta_rho, inv_points):
    arcs = []
    for i in range(len(solution)):
        for route in solution[i]:
            arc = Route_arcs(route, inv_points)
            arcs += arc
    if update == 'Global':
        for arc in arcs:
            for i in range(len(pheromone_mat)):
                pheromone_mat[i][arc[0]][arc[1]] += delta_rho
    elif update == 'Local':
        for arc in arcs:
            for i in range(len(pheromone_mat)):
                pheromone_mat[i][arc[0]][arc[1]] += delta_rho/10
    return pheromone_mat
