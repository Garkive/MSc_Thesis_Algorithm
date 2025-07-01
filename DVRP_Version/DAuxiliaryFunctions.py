#Auxiliary functions for the Main.py script

import copy
import DDestroyOps
import DRepairOps

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
    solution = DDestroyOps.display_routes(routes)
    id_list, solution_id = DDestroyOps.solution_ids(solution, points, inv_points2)
    solution_id_copy = copy.deepcopy(id_list)
    return points2, data2, indices2, inv_points2, fleet, id_list, solution_id, solution_id_copy

def verify_feas(solution, points, inv_points2, dist_mat, data2, fleet, vehicles):
    feas = []
    for i in range(len(solution[0])):
        route = solution[0][i]
        feasible = DRepairOps.feasibility_check(route, points, inv_points2, dist_mat, data2, fleet, vehicles[0][i])
        feas.append(feasible)
    if False in feas:
        return False
    else: 
        return True