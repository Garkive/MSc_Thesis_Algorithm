#Operator Selection Module for both destroy and repair operators

#To do:
#Define the weight system and functions that update the weights according to 
#success or failure of certain operators.
#Define a selection scheme for each operator in each iteration.

import random
import DRepairOps

#Roulette Selection for destroy and repair heuristics
def Roulette_Selection(w_dest, w_rep, dest_heuristics, rep_heuristics, chosen_ops):
    chosen_ops[0] = random.choices(dest_heuristics, weights=w_dest, k=1)[0]
    chosen_ops[1] = random.choices(rep_heuristics, weights=w_rep, k=1)[0]
    return chosen_ops

#Weights update every 100 iterations (for now)
def weights_update(score_dest, score_rep, w_dest, w_rep, teta_dest, teta_rep, aug_scores, r):
    for i in range(len(w_dest)):
        if teta_dest[i] != 0:  # Check for division by zero
            w_dest[i] = w_dest[i] * (1 - r) + r * (score_dest[i] / teta_dest[i])
    for i in range(len(w_rep)):
        if teta_rep[i] != 0:  # Check for division by zero
            w_rep[i] = w_rep[i] * (1 - r) + r * (score_rep[i] / teta_rep[i])
    return w_dest, w_rep

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

#Score update when a solution is accepted
def score_update(score_dest, score_rep, aug_scores, score_case, chosen_ops):
    if True in score_case:
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
    return score_dest, score_rep

def vehicle_selection(route, inv_points, vehicles):
    vehicle = random.choices(vehicles,weights = [1 for v in vehicles], k = 1)[0]
    return vehicle

def Route_arcs(route, inv_points): 
    arcs = []
    auxiliary_list = []
    for i in range(len(route)-1):
        p1 = DRepairOps.find_pos(route[i], inv_points)[auxiliary_list.count(route[i])]
        auxiliary_list.append(route[i])    
        if i+1 != len(route)-1:
            p2 = DRepairOps.find_pos(route[i+1], inv_points)[auxiliary_list.count(route[i+1])]
        else:
            p2 = DRepairOps.find_pos(route[i+1], inv_points)[0]
        arcs.append([p1, p2])
    return arcs


