#Test for insertion methods

import RepairOps
import DestroyOps
import Main

points, data, dist_mat, hub_num, routes, indices = DestroyOps.import_data()

points2, data2, indices2, inv_points2, id_list, solution_id, solution_id_copy = Main.gather_data(points, data, hub_num, indices, routes)

newsol_cost = 0

# removed_req = [70650, 70656, 70840, 70816]
removed_req = [70840, 70816, 70650, 70656]
partial_solution = [[[22, 70838, 70835, 70660, 70662, 70670, 70658, 70653, 70662, 70660, 70835, 70653, 70658, 70812, 70818, 70822, 70670, 70822, 70818, 70830, 70812, 70838, 70666, 70666, 70830, 22]], [[6, 70664, 70671, 70651, 70671, 70664, 70651, 6]]]
chosen_ops = ['Random', 'Regret']

current_sol = RepairOps.RepairOperator(
    hub_num, removed_req, partial_solution, points2, data2, dist_mat, indices2, inv_points2, chosen_ops
)

#Calculate cost of obtained solution
newsol_cost, total_tardiness = RepairOps.solution_cost(current_sol, dist_mat, points, inv_points2, data)

# print('Prev cost: 279040.846')
print('New cost: ', newsol_cost)

#New Issue 
# route = [22, 70830, 70835, 70664, 70658, 70653, 70651, 70835, 70658, 70664, 70816, 70812, 70830, 22]
# rcost, total_tardiness = RepairOps.route_cost(route, dist_mat, points2, inv_points2, data2)
# print('Route Cost: ', rcost)

# #Another
# rcost = 57696.276
# route = [22, 70830, 70835, 70664, 70658, 70653, 70651, 70835, 70658, 70664, 70816, 70812, 70830, 22]
# insertcost = RepairOps.insertion_cost(route, rcost, dist_mat, points2, inv_points2, data2)
# print('Insertion Cost: ', insertcost)