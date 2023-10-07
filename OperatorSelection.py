#Operator Selection Module for both destroy and repair operators

#To do:
#Define the weight system and functions that update the weights according to 
#success or failure of certain operators.
#Define a selection scheme for each operator in each iteration.

import random

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

    
    
    


