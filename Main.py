import DestroyOps
import RepairOps
import time
import copy

max_iter = 10
time_limit = 10000

points, data, dist_mat, hub_num, routes, indices = DestroyOps.import_data()
solution = DestroyOps.display_routes(routes)
id_list, solution_id = DestroyOps.solution_ids(solution, points)

solution_id_copy = copy.deepcopy(id_list)

start_time = time.time()
current_time = 0
current_iter = 1
best_sol = solution_id
best_sol_cost, initial_tardiness = RepairOps.solution_cost(best_sol, dist_mat, points, data)

while current_iter <= max_iter and current_time < time_limit:
    print('Iteration:', current_iter, flush=True)
    
    partial_solution, removed_req = DestroyOps.DestroyOperator(
        solution_id_copy, best_sol, points, data, dist_mat, hub_num, routes, indices
    )
    
    time22 = time.time()
    current_sol = RepairOps.Greedy_Insertion(
        hub_num, removed_req, partial_solution, points, data, dist_mat, indices
    )
    time33 = time.time()
    time3 = time33 - time22
    print('Time 3:', time3)

    newsol_cost, total_tardiness = RepairOps.solution_cost(current_sol, dist_mat, points, data)
    if newsol_cost < best_sol_cost:
        best_sol_cost = newsol_cost
        best_sol = current_sol
        # print('Solution Improved - Cost:', best_sol_cost, flush=True)
        # print('Solution Tardiness:', total_tardiness, flush=True)

    current_time = time.time() - start_time
    current_iter += 1

best_sol_cost, total_tardiness = RepairOps.solution_cost(best_sol, dist_mat, points, data)

print('Cost of final solution is:', best_sol_cost)
print('Total tardiness of solution is:', total_tardiness)
print('Total time:', current_time)