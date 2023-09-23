# -*- coding: utf-8 -*-

import RepairOps
import DestroyOps
import Main

costumer = 70840
partial_solution = [[[22, 70653, 70670, 70670, 70816, 70818, 70653, 70818, 70816, 70662, 70666, 70666, 70662, 22], [22, 70830, 70838, 70835, 70838, 70651, 70658, 70664, 70651, 70658, 70664, 70835, 70830, 70671, 70671, 22]], [[6, 70822, 70822, 70656, 70660, 70650, 70656, 70660, 70650, 6]]]
hub_num = 2
points, data, dist_mat, hub_num, routes, indices = DestroyOps.import_data()
points, data, indices, inv_points, id_list, solution_id, solution_id_copy = Main.gather_data(points, data, hub_num, indices, routes)


for i in range(hub_num):
    for route_ind, route in enumerate(partial_solution[i]):
        rcost, total_tardiness = RepairOps.route_cost(route, dist_mat, points, inv_points, data) 
        temp_route_p = route.copy()
        feasibility_p = RepairOps.feasibility_check(temp_route_p, points, inv_points, dist_mat, data) 
        print('Feasible initial route? ', feasibility_p)
        if feasibility_p:
            for j in range(1, len(route)):
                temp_route_p.insert(j, costumer)
                feasibility_d = RepairOps.feasibility_check(temp_route_p, points, inv_points, dist_mat, data)
                print('Route: ', temp_route_p)
                print('Feasible 1? ', feasibility_d)
                if feasibility_d:
                    for k in range(j+1, len(route)):
                        temp_route_d = temp_route_p.copy()
                        temp_route_d.insert(k, costumer)
                        feasibility = RepairOps.feasibility_check(temp_route_d, points, inv_points, dist_mat, data)
                        print('Route: ', temp_route_d)
                        print('Feasible 2? ', feasibility)
                        if feasibility:
                            icost = RepairOps.insertion_cost(temp_route_d, rcost, dist_mat, points, inv_points, data)
                            insert_list.append((icost, i, route_ind, j, k))                    
                        temp_route_d.pop(k)                          
                temp_route_p.pop(j) 
                
print('Insert List: ', insert_list)

#Feasibility check correction test
# temp_route = [6, 70822, 70822, 70656, 70660, 70650, 70656, 70660, 70650, 70840, 6]
# feasibility = RepairOps.feasibility_check(temp_route, points, inv_points, dist_mat, data)