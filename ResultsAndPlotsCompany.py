# -*- coding: utf-8 -*-
"""
Created on Tue May  2 12:59:51 2023

@author: João Moura
"""
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
import csv
import InitialSolution
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

travel_distances, routes, vehicle_remaining, data, indices, points, hub_num, DistMat, couriers, point, hub_pairs, service_time, df_hub, lat, long, lat_pu, long_pu, lat_do, long_do, lat_hub, long_hub = InitialSolution.Results()

#Plot costumer points
plt.plot(lat_pu,long_pu, 'bo')
plt.plot(lat_do,long_do, 'ro')
plt.plot(lat_hub,long_hub, 'ko')

for i in range(points.shape[0]):
      plt.annotate('%d'%i, (points.iloc[i][2], points.iloc[i][1]), color='black')
plt.title('Routes')
plt.xlabel('Latitude')
plt.ylabel('Longitude')

for i in range(hub_num):
    if i == 0:
        plotstyle = 'yo'
    else:
        plotstyle = 'ro'
    for j in range(len(routes[i])-1):
        if j == 0:
            plotlabel = str('Route % s' % i)
        else:
            plotlabel = None
        x_values = [lat[routes[i][j]],lat[routes[i][j+1]]] 
        y_values = [long[routes[i][j]],long[routes[i][j+1]]]
        plt.plot(x_values,y_values, plotstyle, linestyle = '--', label = plotlabel)
plt.plot(lat_hub,long_hub, 'ko', label = 'Hubs')
plt.legend()
plt.grid()
plt.show()

hub = 0
for i in routes:
    
    print('Hub', hub, 'route: ')
   
    for x in i:
        print (x,end=" ")
    print("\n" 'With total travel distance: ' + str('%s' % int(travel_distances[hub])) + "\n")
    hub += 1


#Save relevant information in .csv format, to be used later
if local == 1:
    os.chdir('C:/Users/exemp/Desktop/Tese de Mestrado/Código/CSV_Files')
    
data.to_csv('Processed_data.csv') #Overall data DataFrame

pd_info = pd.concat([points['id'], point], axis=1, ignore_index=False) 
pd_info.to_csv('Pickup_delivery_info.csv', index=False) #Pickup and Delivery ids, lat/long values, weight and volumetric loads
np.savetxt('Distance_matrix.csv', DistMat, delimiter=',')

#Obtained initial solution
with open('Initial_solution.csv', 'w', newline='') as f:
    # create a CSV writer object
    writer = csv.writer(f)
    # write the data to the CSV file
    writer.writerows(routes)

#Associated Pickups and Deliveries
with open('Pickup_delivery_pairs.csv', 'w', newline='') as f:
    # create a CSV writer object
    writer = csv.writer(f)
    # write the data to the CSV file
    writer.writerows(indices)