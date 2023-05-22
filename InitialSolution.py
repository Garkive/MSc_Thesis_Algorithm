# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 00:02:11 2022

@author: João Moura
"""

import copy
import DataProcessing 


#0 for home pc, 1 for laptop
local = 1
if local == 1:
    path = 'exemp' 
elif local == 0:
    path = 'João Moura'

#0 for first data, 1 for second
entry_data = 0
if entry_data == 0:
    dados = 'Dados'
elif entry_data == 1:
    dados = 'Dados2'

service_time = 10*60 #10min
#Mota = 15 m/s
#Carrinha = 10 m/s



def select_courier(tryfastervehicle, next_costumer, hub_id, cour, point):
    cour_bike = cour[cour[4] == 1]
    cour_van = cour[cour[4] == 4]
    if tryfastervehicle == True:
        vehicle = cour_bike.index[0]
        veh_spd = 15 
    else:
        if point.iloc[next_costumer]['weight']*2 < cour_bike.iloc[0]['weight_cap'] and point.iloc[next_costumer]['volume']*2 < cour_bike.iloc[0]['volume_cap']:
             vehicle = cour_bike.index[0]
             veh_spd = 15
        else:
             vehicle = cour_van.index[0]
             veh_spd = 10
    
    return vehicle, veh_spd

#Find costumer number from Pickup+Delivery id number
def find_pos(i_d, points):    
    pos = [i for i,x in enumerate(points['id']) if x==i_d]    
    return pos

#Find id number of a Pickup or Delivery
def find_id(pos, points):
    i_d = points.iloc[pos]['id']
    return i_d


#Constrains to consider:
    #Maximum load - volume and weight
    #Time Windows for the costumers
    #Multiple depots
    #Heterogeneous Fleet
    #The packages must be delivered by the vehicle that picks them up
    

def get_nearest_index(data,tryfastervehicle, costumers, current_index, current_load, current_vol, current_time, current_vehicle, DistMat, hub_costum, indices, point, hub_id,cour, service_time, vehicle_spd, delivery_list, i, points, hub_num, df_hub):
    nearest_ind = None
    nearest_distance = None
    ind_type = None
    veh_spd = vehicle_spd
    for next_costumer in costumers:
        
        if next_costumer < len(indices): #Pickup or delivery
            e_time = 'end_time_pu'
            s_time = 'start_time_pu' 
            p_or_d = 'p'
        else:
            e_time = 'end_time_do'
            s_time = 'start_time_do'
            p_or_d = 'd'

        
        if current_index == i:
            vehicle, veh_spd = select_courier(tryfastervehicle,next_costumer, hub_id, cour, point)
            current_vehicle = vehicle

        # if current_index == 3:
        #     print(veh_spd)
        #     print(current_load)
        #     print(current_load + point.iloc[next_costumer]['weight'] > cour[cour.index == current_vehicle]['weight_cap'].iloc[0])
             
        #Weight constraint
        if current_load + point.iloc[next_costumer]['weight'] > cour[cour.index == current_vehicle]['weight_cap'].iloc[0]:
            continue
        
        #Volume constraint
        if current_vol + point.iloc[next_costumer]['volume'] > cour[cour.index == current_vehicle]['volume_cap'].iloc[0]:
            continue
        
        dist = DistMat[current_index][next_costumer]
        wait_time = max(data.iloc[find_pos(find_id(next_costumer,points),points)[0]-hub_num][s_time] - current_time - dist/veh_spd,0)
       
        #Check if it can come back to the hub before it closes
        if int(current_time + service_time + dist/veh_spd + DistMat[next_costumer][find_pos(hub_id,points)]/veh_spd + wait_time) > int(df_hub[5][find_pos(hub_id,points)]*60*60):
            continue
        #Check due time
        if current_time + dist/veh_spd > data[e_time].loc[find_id(next_costumer,points)]:
            continue
        # if current_index == 3:
        #     print(costumers)
        # if current_index == 3 and next_costumer == 158:
        #     print(current_time)
        #     print(current_load + point.iloc[next_costumer]['weight'] > cour[cour.index == current_vehicle]['weight_cap'].iloc[0])
        #     print(current_vol + point.iloc[next_costumer]['volume'] > cour[cour.index == current_vehicle]['volume_cap'].iloc[0])
        #     print(int(current_time + service_time + dist/veh_spd + DistMat[next_costumer][find_pos(hub_id)]/veh_spd + wait_time) > int(df_hub[5][find_pos(hub_id)]*60*60))
        #     print(current_time + dist/veh_spd > data[e_time].loc[find_id(next_costumer,points)])
            
        #Check if pickup can be made, considering current delivery list
        if p_or_d == 'p':
            pseudo_route = [current_index,next_costumer]
            pseudo_delivery_list = copy.deepcopy(delivery_list)
            aug_pseudo_route, time, feasible = modular_NN(current_index,DistMat,pseudo_delivery_list,pseudo_route, current_time, service_time, data, veh_spd, s_time,hub_id, i, points, hub_num, df_hub)

            if feasible == False:
                continue
            
        if nearest_distance is None or DistMat[current_index][next_costumer] < nearest_distance:
            nearest_distance = dist     
            nearest_ind = next_costumer
            ind_type = p_or_d
            
        
    return current_vehicle, nearest_ind, ind_type, veh_spd

#Modular nearest index check for the modular NN 
def modular_nearest_index(pseudo_route, pseudo_delivery_list, DistMat, ind_type, current_index, service_time, time, s_time, data, veh_spd,points):
    nearest_dist = None
    feasible = True
    pos_index = 1
    e_time = 'end_time_do'

    if ind_type == 'p':
        pos_index = 0
        
    for delivery in pseudo_delivery_list:
        
        dist = DistMat[find_pos(current_index,points)[pos_index]][find_pos(delivery,points)[1]]
        #Check due time
        if time + dist/veh_spd > data[e_time].loc[delivery]:
            feasible = False
            nearest_ind = None
            break
        
        if nearest_dist is None or dist < nearest_dist:
            nearest_dist = DistMat[find_pos(current_index,points)[pos_index]][find_pos(delivery,points)[1]]
            nearest_ind = delivery

    return nearest_ind, ind_type, pos_index, feasible
        
#Modular NN to verify feasibility of insertion of a new pickup + delivery pair into current courier route
def modular_NN(current_index,DistMat,pseudo_delivery_list,pseudo_route, current_time, service_time, data, veh_spd, s_time,hub_id, i, points, hub_num, df_hub):

    dist = DistMat[pseudo_route[0]][pseudo_route[1]]
    wait_time = max(data.iloc[pseudo_route[1]-hub_num]['start_time_pu'] - current_time - dist/veh_spd,0)
    time = current_time + dist/veh_spd + service_time + wait_time

    # print('modular_NN time: ',time)
    current_index = find_id(pseudo_route[1],points)  
    ind_type = 'p'
    pseudo_delivery_list.append(current_index)
    feasible = True
    while len(pseudo_delivery_list) != 0 and feasible != False:
        nearest_ind, ind_type, pos_index, feasible = modular_nearest_index(pseudo_route, pseudo_delivery_list, DistMat, ind_type, current_index, service_time, time, s_time, data, veh_spd,points)
        if feasible == False:
            break

        pseudo_route.append(find_pos(nearest_ind,points)[1])
        dist = DistMat[find_pos(current_index,points)[pos_index]][find_pos(nearest_ind,points)[1]]
        wait_time = max(data.iloc[find_pos(nearest_ind,points)[0]-hub_num][s_time] - time - dist/veh_spd,0)
        time += dist/veh_spd + service_time + wait_time
        current_index = nearest_ind
        ind_type = 'd'
        pseudo_delivery_list.remove(nearest_ind)


    time += DistMat[find_pos(current_index,points)[pos_index]][find_pos(hub_id,points)]/veh_spd
    if time > int(df_hub[5][find_pos(hub_id,points)]*60*60):
        feasible = False
    
    return pseudo_route, time, feasible



def NNs(hub_pairs, i, couriers, indices, data, point, DistMat, service_time, points, hub_num, df_hub): 
    current_index = i
    current_load = 0
    current_vol = 0
    current_time = 0
    travel_dist = 0    
    vehicle_spd = 0
    tryfastervehicle = False
    nonecounter = 0
    route = [i]
    hub_id = points.iloc[i]['id']
    cour = couriers[couriers[5] == hub_id]  
    vehicle_num = len(cour)
    print('Initial vehicle number:',vehicle_num)
    current_vehicle = None
    costumers = []
    delivery_list = []
    
    for j in range(len(hub_pairs[i])):
        costumers.append(indices[hub_pairs[i][j]][0])
    while len(costumers) != 0 and vehicle_num != 0 and nonecounter < 3: #Mudar != 0
        
        #Attempt to allocate faster vehicle if current attempts fail to satisfy costumer time window
        if nonecounter > 1: 
            tryfastervehicle = True

        vehicle, nearest_ind,ind_type, veh_spd = get_nearest_index(data,tryfastervehicle, costumers, current_index, current_load, current_vol, current_time,current_vehicle, DistMat, hub_pairs, indices, point, hub_id, cour, service_time, vehicle_spd, delivery_list, i, points, hub_num, df_hub)

        if nearest_ind is None:
            nonecounter += 1
            travel_dist += DistMat[current_index][find_pos(hub_id,points)]
            current_load = 0
            current_vol = 0
            current_time = 0
            route.append(i)
            delivery_list = []
            current_index = i
            cour.drop(vehicle, axis = 0) #Vehicle used
            vehicle_num -= 1
            print('Speed of the used vehicle:', veh_spd)                
            print('Current vehicle number:', vehicle_num)
        else:
            nonecounter = 0
            current_load += point.iloc[nearest_ind]['weight']
            current_vol += point.iloc[nearest_ind]['volume']
            current_vehicle = vehicle
            vehicle_spd = veh_spd


            dist = DistMat[current_index][nearest_ind]
            if ind_type == 'p':
                s_time = 'start_time_pu' 
            else:
                s_time = 'start_time_do'
            wait_time = max(data.iloc[find_pos(find_id(nearest_ind,points),points)[0]-hub_num][s_time] - current_time - DistMat[current_index][nearest_ind]/veh_spd,0)
            current_time += dist/veh_spd + wait_time + service_time
            costumers.remove(nearest_ind)
            if ind_type == 'p':
                costumers.append(find_pos(find_id(nearest_ind,points),points)[1])
                delivery_list.append(find_id(nearest_ind,points))
            else: 

                delivery_list.remove(find_id(nearest_ind,points))
            travel_dist += dist
            route.append(nearest_ind)
            current_index = nearest_ind
        
        # if i ==1:
        #     print(costumers)
    travel_dist += DistMat[current_index][find_pos(hub_id,points)]
    route.append(i)
    cour.drop(vehicle, axis = 0) 
    print('Speed of the used vehicle:', veh_spd)
    vehicle_num -= 1   
    print('Final vehicle number:',vehicle_num)
    return travel_dist, route, vehicle_num

def Results():
    data, indices, points, hub_num, DistMat, couriers, point, hub_pairs, service_time, df_hub, lat, long, lat_pu, long_pu, lat_do, long_do, lat_hub, long_hub = DataProcessing.processed_data()
    #Final results presented
    travel_distances = []
    routes = []
    vehicle_remaining = []
    for i in range(hub_num):
        travel_dist, route, vehicle_num = NNs(hub_pairs, i, couriers, indices, data, point, DistMat, service_time, points, hub_num, df_hub)
        travel_distances.append(travel_dist)
        routes.append(route)
        vehicle_remaining.append(vehicle_num)
    return travel_distances, routes, vehicle_remaining, data, indices, points, hub_num, DistMat, couriers, point, hub_pairs, service_time, df_hub, lat, long, lat_pu, long_pu, lat_do, long_do, lat_hub, long_hub 
