#Module to import and preprocess benchmark data from Li & Lim benchmarks 

#TASK NO ; X ; Y ; DEMAND ; EARLIEST TIME ; LATEST TIME ; SERVICE TIME ; PICKUP (SIBLING NO) ; DELIVERY (SIBLING NO)

import pandas as pd
import numpy as np
from collections import deque

def import_and_process_data(file):
    # Read the data from the txt file
    
    #Laptop and desktop paths
    #Dataset = pd.read_csv('C:\\Users\\exemp\\Desktop\\Benchmark datasets\\pdp_100\\' + file, sep='\t', header=None, skiprows=1)
    Dataset = pd.read_csv('C:\\Users\\João Moura\\Desktop\\Benchmark datasets\\pdp_100\\' + file, sep='\t', header=None, skiprows=1)

    # Set column names for the DataFrame
    column_names = ['task', 'X', 'Y', 'Demand', 'earliest_time', 'latest_time', 'service_time', 'Pickup', 'Delivery']
    Dataset.columns = column_names

    # Read only the first line from the txt file
    #DatasetInfo = pd.read_csv('C:\\Users\\exemp\\Desktop\\Benchmark datasets\\pdp_100\\' + file, sep='\t', header=None, nrows=1)
    DatasetInfo = pd.read_csv('C:\\Users\\João Moura\\Desktop\\Benchmark datasets\\pdp_100\\' + file, sep='\t', header=None, nrows=1)

    # Set column names for the DataFrame
    column_names = ['num_vehicles', 'vehicle_capacity', 'vehicle_speed']
    DatasetInfo.columns = column_names
    
    veh_capacity = DatasetInfo.iloc[0][1]
    max_vehicles = DatasetInfo.iloc[0][0]
    
    hub_num = 1
    n = int((len(Dataset) - 1)/2)
    auxiliary_list = deque()
    indices = [[0]]
    ids = deque([0])
    counter = 1
    for i in range(1, len(Dataset)):
        if Dataset.iloc[i][0] not in auxiliary_list:
            if Dataset.iloc[i][7] != 0:
                indices.append([Dataset.iloc[Dataset.iloc[i][7]][0],Dataset.iloc[i][0]])
                auxiliary_list.append(Dataset.iloc[i][0])
                auxiliary_list.append(Dataset.iloc[Dataset.iloc[i][7]][0])
                ids.append(counter)
                counter += 1
            elif Dataset.iloc[i][8] != 0:
                indices.append([Dataset.iloc[i][0],Dataset.iloc[Dataset.iloc[i][8]][0]])
                auxiliary_list.append(Dataset.iloc[i][0])
                auxiliary_list.append(Dataset.iloc[Dataset.iloc[i][8]][0])
                ids.append(counter)
                counter += 1
        
    task_ids = [0]*len(Dataset)
    
    for i in range(1,n+1):
        task_ids[indices[i][0]] = i
        task_ids[indices[i][1]] = i
        
        
        
    # Extract desired columns to create a new dataset
    columns_to_extract = ['X', 'Y', 'Demand']
    points = Dataset[columns_to_extract]
        
    volume = [0]*len(Dataset)    
    
    # Adding a new column
    new_column_name = 'id'  # Name of the new column
    volume_name = 'volume'
    points[new_column_name] = task_ids
    points[volume_name] = volume
    points = points[['id' ,'X','Y', 'Demand', 'volume']]
    points.rename(columns={'Y': 'latitude'}, inplace=True)
    points.rename(columns={'X': 'longitude'}, inplace=True)
    points.rename(columns={'Demand': 'weight'}, inplace=True)
    points.loc[:, 'weight'] *= -1 
    points['service_time'] = Dataset['service_time']
    
    dist_mat = np.zeros((len(Dataset),len(Dataset)))
    
    #Calculate Distance Matrix - Euclidean Distance
    for i in range(len(dist_mat)):
        for j in range(len(dist_mat)):
            
            dist_mat[i][j] = np.linalg.norm((float(Dataset.iloc[i][2]) - float(Dataset.iloc[j][2]), float(Dataset.iloc[i][1]) - float(Dataset.iloc[j][1])))
            dist_mat[j][i] = dist_mat[i][j]    
    
    
    #Find id number of a Pickup or Delivery
    def find_id(pos, points):
        i_d = points['id'][pos]
        return i_d
        
    #Find costumer number from Pickup+Delivery id number
    def find_pos(i_d,  inv_points):    
        pos = inv_points[i_d]
        return pos
    
    task_to_id = {}
    for idx, tasks in enumerate(indices):
        if len(tasks) == 1:
            depot = tasks[0]
            task_to_id[depot] = idx
        else:
            pickup_task, delivery_task = tasks
            task_to_id[pickup_task] = idx
            task_to_id[delivery_task] = idx
    
    inv_points2 = []
    solution_id = []
    for i in range(n+1):
        if i >= hub_num:
            solution_id.append(i)
        # entries = points[points['id'] == i]
        # print('Entries: ',entries)
        
        # if len(entries) != 1:
        #     print('Entry 0: ',entries.index[0])
        #     print('Entry 1: ',entries.index[1])
        #     inv_points2.append((entries.index[0], entries.index[1]))
        # else:
        #     inv_points2.append((entries.index[0], 0))
        
    
    for i in range(len(indices)):
        if len(indices[i]) != 1:
            inv_points2.append((indices[i][0], indices[i][1]))
        else:
            inv_points2.append((indices[i][0], 0))
    inv_points2 = dict(enumerate(inv_points2))
    
    initial_data = {
        'id': [find_id(indices[1][0], points)],
        'start_time_pu': [Dataset.iloc[indices[1][0]][4]],
        'end_time_pu': [Dataset.iloc[indices[1][0]][5]],
        'start_time_do': [Dataset.iloc[indices[1][1]][4]],
        'end_time_do': [Dataset.iloc[indices[1][1]][5]],
        'weight': [-Dataset.iloc[indices[1][0]][3]],
        'volume': [0],
        'latitude_pu': [Dataset.iloc[indices[1][0]][1]],
        'longitude_pu': [Dataset.iloc[indices[1][0]][2]],
        'latitude_do': [Dataset.iloc[indices[1][1]][1]],
        'longitude_do': [Dataset.iloc[indices[1][1]][2]],
    }
    
    data = pd.DataFrame(initial_data)
        
    for i in range(2,n+1):
        row_data = {
            'id': find_id(indices[i][0], points),
            'start_time_pu': Dataset.iloc[indices[i][0]][4],
            'end_time_pu': Dataset.iloc[indices[i][0]][5],
            'start_time_do': Dataset.iloc[indices[i][1]][4],
            'end_time_do': Dataset.iloc[indices[i][1]][5],
            'weight': -Dataset.iloc[indices[i][0]][3],
            'volume': 0,
            'latitude_pu': Dataset.iloc[indices[i][0]][1],
            'longitude_pu': Dataset.iloc[indices[i][0]][2],
            'latitude_do': Dataset.iloc[indices[i][1]][1],
            'longitude_do': Dataset.iloc[indices[i][1]][2],
        }
        
        # Convert the new row into a DataFrame
        new_row = pd.DataFrame([row_data])
        
        # Concatenate the original DataFrame with the new row DataFrame
        data = pd.concat([data, new_row], ignore_index=True)
    data.set_index('id', inplace=True)
    
    
    
    
    return points, data, indices, inv_points2, dist_mat, hub_num, solution_id, veh_capacity, max_vehicles






