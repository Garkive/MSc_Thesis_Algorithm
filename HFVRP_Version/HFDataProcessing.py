
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from more_itertools import locate

#0 for home pc, 1 for laptop
local = 0
if local == 1:
    path = 'exemp' 
elif local == 0:
    path = 'João Moura'

#0 for first data, 1 for second
entry_data = 1
if entry_data == 0:
    dados = 'Dados'
elif entry_data == 1:
    dados = 'Dados2'

service_time = 10*60 #10min
#Mota = 15 m/s
#Carrinha = 10 m/s

def import_data():
    #Read csv files 
    cols_pu = pd.read_csv('C:/Users/'+path+'/Desktop/Tese de Mestrado/'+dados+'/pu-points.csv',sep = ';', nrows=0).columns.tolist()
    df_pu = pd.read_csv('C:/Users/'+path+'/Desktop/Tese de Mestrado/'+dados+'/pu-points.csv',sep = ';', header=None, skiprows=[0])
    
    cols_do = pd.read_csv('C:/Users/'+path+'/Desktop/Tese de Mestrado/'+dados+'/do-points.csv',sep = ';', nrows=0).columns.tolist()
    df_do = pd.read_csv('C:/Users/'+path+'/Desktop/Tese de Mestrado/'+dados+'/do-points.csv',sep = ';', header=None, skiprows=[0])
    
    cols_hub = pd.read_csv('C:/Users/'+path+'/Desktop/Tese de Mestrado/'+dados+'/hubs_aug.csv',sep = ';', nrows=0).columns.tolist()
    df_hub = pd.read_csv('C:/Users/'+path+'/Desktop/Tese de Mestrado/'+dados+'/hubs_aug.csv',sep = ';', header=None, skiprows=[0])
    
    objects = pd.read_csv('C:/Users/'+path+'/Desktop/Tese de Mestrado/'+dados+'/objects.csv',sep = ';', header=None, skiprows=[0])
    
    couriers = pd.read_csv('C:/Users/'+path+'/Desktop/Tese de Mestrado/'+dados+'/couriers.csv',sep = ';', header=None, skiprows=[0])
    
    veh_type = pd.read_csv('C:/Users/'+path+'/Desktop/Tese de Mestrado/'+dados+'/vehicle_types.csv',sep = ';', header=None, skiprows=[0])
    
    if entry_data == 1:
        def stringtoiso(x):
            date = datetime.strptime(x, '%d/%m/%Y %H:%M')
            date = date.isoformat()
            return date
        df_pu[4] = df_pu[4].apply(stringtoiso)
        df_do[4] = df_do[4].apply(stringtoiso)
        
        def stringtoiso2(x):
            date = datetime.strptime(x, '%d/%m/%Y %H:%M')
            date = date.isoformat()
            return date
        df_pu[5] = df_pu[5].apply(stringtoiso2)
        df_do[5] = df_do[5].apply(stringtoiso2)
    return cols_pu, df_pu, cols_do, df_do, cols_hub, df_hub, objects, couriers, veh_type


def haversine(coord1: object, coord2: object):

    # Coordinates in decimal degrees (e.g. 2.89078, 12.79797)
    lon1, lat1 = coord1
    lon2, lat2 = coord2

    R = 6371000  # radius of Earth in meters
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    meters = R * c  # output distance in meters
    km = meters / 1000.0  # output distance in kilometers

    meters = round(meters, 3)
    km = round(km, 3)

    return meters

def preprocessing(df_pu, df_do, df_hub, objects, couriers):
    
    
    objects = objects.rename(columns={0:"id", 1:"weight", 2:"volume"})
    objects = objects.set_index('id')
    
    couriers = couriers.drop(1, axis = 1)
    couriers = couriers.rename(columns={0:"id", 2:"volume_cap", 3:"weight_cap"})
    couriers = couriers.set_index('id')

    pu_tw = []
    do_tw = []
    pu_id = []
    do_id = []
    
    for i in range(len(df_pu)):
        
        #Pickups first
        start_d = datetime.fromisoformat(df_pu[4][i])
        end_d = datetime.fromisoformat(df_pu[5][i])
        pu_id.append(df_pu[0][i])
        
        start_time = start_d.hour*60*60+start_d.minute*60+start_d.second #Start time in seconds
        end_time = end_d.hour*60*60+end_d.minute*60+end_d.second #End time in seconds
        
        pu_tw.append([start_time, end_time]) #Create time window array
        
        #Deliveries second
        start_d = datetime.fromisoformat(df_do[4][i])
        end_d = datetime.fromisoformat(df_do[5][i])
        do_id.append(df_do[0][i])
        
        start_time = start_d.hour*60*60+start_d.minute*60+start_d.second #Start time in seconds
        end_time = end_d.hour*60*60+end_d.minute*60+end_d.second #End time in seconds
        
        do_tw.append([start_time, end_time]) #Create time window array
        
    pu_id = np.array(pu_id)
    do_id = np.array(do_id)
    pu_tw = np.array(pu_tw)
    do_tw = np.array(do_tw)
    
    df1_pu = pd.DataFrame(pu_id, columns=['id'])
    df2_pu = pd.DataFrame(pu_tw, columns=['start_time_pu', 'end_time_pu'])
    pu = df1_pu.join(df2_pu, how = 'outer')
    
    df1_do = pd.DataFrame(do_id, columns=['id'])
    df2_do = pd.DataFrame(do_tw, columns=['start_time_do', 'end_time_do'])
    do = df1_do.join(df2_do, how = 'outer')
    
    pu = pu.set_index('id')
    do = do.set_index('id')
    
    data = pu.join(do, how = 'outer' )
    data = data.join(objects, how = 'outer') #Add objects to the pickup dataframe
    
    #Select costumer latitude and longitude points
    
    #Hide real data
    # long_pu = (np.array(df_pu[3])+9.25)*100
    # lat_pu = (np.array(df_pu[2])-38.75)*100
    # long_do = (np.array(df_do[3])+9.25)*100
    # lat_do = (np.array(df_do[2])-38.75)*100
    # long_hub = (np.array(df_hub[3])+9.25)*100
    # lat_hub = (np.array(df_hub[2])-38.75)*100
    
    long_pu = np.array(df_pu[3])
    lat_pu = np.array(df_pu[2])
    long_do = np.array(df_do[3])
    lat_do = np.array(df_do[2])
    long_hub = np.array(df_hub[3])
    lat_hub = np.array(df_hub[2])
    
    long = np.concatenate((np.concatenate((long_hub, long_pu)),long_do))
    lat = np.concatenate((np.concatenate((lat_hub, lat_pu)),lat_do))
    
    DistMat = np.zeros((len(long),len(long)))
    
    # #Calculate Distance Matrix - Euclidean Distance
    # for i in range(len(long)):
        
    #     for j in range(len(long)):
            
    #         DistMat[i][j] = np.linalg.norm((float(lat[i]) - float(lat[j]), float(long[i]) - float(long[j])))
    #         DistMat[j][i] = DistMat[i][j]
    
    #Distance Matrix - Haversine Formula
    for i in range(len(long)):
        for j in range(len(long)):
                        DistMat[i][j] = haversine([lat[i],long[i]],[lat[j],long[j]])
                        DistMat[j][i] = DistMat[i][j]
       
    lat_pu = pd.DataFrame(lat_pu, columns=['latitude_pu'])
    pu_df = lat_pu.join(pd.DataFrame(long_pu, columns=['longitude_pu']), how = 'outer')
    pu_df = df1_pu.join(pu_df, how = 'outer')
    pu_df = pu_df.set_index('id')
    
    lat_do = pd.DataFrame(lat_do, columns=['latitude_do'])
    do_df = lat_do.join(pd.DataFrame(long_do, columns=['longitude_do']), how = 'outer')
    do_df = df1_do.join(do_df, how = 'outer')
    do_df = do_df.set_index('id')
    
    position_df = pu_df.join(do_df, how = 'outer')
    
    
    data = data.join(position_df, how = 'outer')
    
    hub_id = np.array(df_hub[0])
    hub_num = len(hub_id)
    
    ids = np.concatenate((hub_id,np.concatenate((pu_id, do_id))))
    
    ids = pd.Series(ids)
    long = pd.Series(long)
    lat = pd.Series(lat)
    
    n = data.shape[0]
    
    points = pd.concat([ids, long, lat], axis = 1)
    points = points.rename(columns={0:"id", 1:"longitude", 2:"latitude"})
    point = points.set_index('id')
    point = point.join(objects, how = 'outer')
    point = point.reset_index(drop = True)
    for i in range(data.shape[0]-1+hub_num):
        point['weight'].loc[n+1+i] = point['weight'].loc[n+1+i]*-1
        point['volume'].loc[n+1+i] = point['volume'].loc[n+1+i]*-1
    #Plot costumer points
    plt.plot(lat_pu,long_pu, 'bo', label='pickups')
    plt.plot(lat_do,long_do, 'ro', label='deliveries')
    plt.plot(lat_hub,long_hub, 'ko', label='depots')
    
    for i in range(points.shape[0]):
         plt.annotate('%d'%i, (points.iloc[i][2]+0.4, points.iloc[i][1]+0.3), color='black')
    plt.title('Costumer Points')
    # plt.xlabel('Latitude')
    # plt.ylabel('Longitude')
    plt.legend()
    plt.grid()
    plt.show()
    
    #Get pickup and delivery pairs by index
    indices = []
    for i in range(len(long_pu)+hub_num):
        ind = locate(ids, lambda x: x == ids[i])
        indices.append(list(ind))

    return data, indices, points, hub_num, DistMat, couriers, point, lat, long, lat_pu, long_pu, lat_do, long_do, lat_hub, long_hub

#Assigns each P-D pair to a depot
def grouping_phase(data, hub_num, indices, DistMat, n, points):
    Dist_hub = []
    for i in range(hub_num):
        Dist = []
        for j in range(hub_num, n+hub_num): #Mudar aqui para n+1 ou n+hub_num
            PP = indices[j][0]
            DP = indices[j][1]
            Dist.append(DistMat[i][PP] + DistMat[i][DP])

        Dist_hub.append(Dist)
    depot_ind = []

    #Dados = n; Dados2 = n-hub_num (não sei como)
    for j in range(n):   
        
        D = []
        for i in range (hub_num):
            D.append(Dist_hub[i][j])
            
        depot_ind.append(np.argmin(D))
        
    pair_df = pd.DataFrame(indices)  
    assign_hub = pd.Series(depot_ind, name = 'hub')  
    for i in range(hub_num):
        assign_hub[n+i] = ''
    assign_hub = assign_hub.shift(periods=hub_num)
    assign_hub = pair_df.join(assign_hub, how= 'outer')                    
    for i in range(hub_num):
        assign_hub = assign_hub.drop(i)
        
    hub_pairs = []
    for i in range(hub_num):
        index_names = assign_hub[assign_hub['hub'] == i].index
        hub_pairs.append(index_names)  
        
    costum_id = []
    hub_costum = []
    for i in range(len(hub_pairs)):
        for j in range(len(hub_pairs[i])):
            costum_id.append(points.iloc[hub_pairs[i][j]]['id'])
        hub_costum.append(costum_id)    
        
    return depot_ind, hub_pairs,Dist_hub,D, hub_costum
 
def processed_data():
    cols_pu, df_pu, cols_do, df_do, cols_hub, df_hub, objects, couriers, veh_type = import_data()
    data, indices, points, hub_num, DistMat, couriers, point, lat, long, lat_pu, long_pu, lat_do, long_do, lat_hub, long_hub = preprocessing(df_pu, df_do, df_hub, objects, couriers) 
    n = data.shape[0]      
    depot_ind, hub_pairs, Dist_hub, D, hub_costum = grouping_phase (data, hub_num, indices, DistMat, n, points)
    service_time = 600
    return data, indices, points, hub_num, DistMat, couriers, point, hub_pairs, service_time, df_hub, lat, long, lat_pu, long_pu, lat_do, long_do, lat_hub, long_hub
