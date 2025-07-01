#Module defining the functions for the Simulated Annealing acceptance criteria

import math

#Simple simulated annealing
def SimulatedAnnealing(newsol_cost, best_sol_cost, temperature, cooling_rate):
    # print('Generated Solution Cost: ', newsol_cost)
    # print('Global Best Solution Cost: ', best_sol_cost)
    if newsol_cost < best_sol_cost:
        return 1.0
    delta = newsol_cost - best_sol_cost
    accept_prob = math.exp(-delta / temperature)
    return accept_prob

def calculate_starting_temperature(best_sol_cost, w):
    max_allowed_change = w * best_sol_cost
    starting_temperature = max_allowed_change / math.log(2)
    return starting_temperature