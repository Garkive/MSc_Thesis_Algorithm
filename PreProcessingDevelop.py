# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 15:04:07 2022

@author: João Paulo
"""
import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
from datetime import datetime

#Read csv files 
cols_pu = pd.read_csv('C:/Users/João Moura/Desktop/Tese de Mestrado/Dados/pu-points.csv',sep = ';', nrows=0).columns.tolist()
df_pu = pd.read_csv('C:/Users/João Moura/Desktop/Tese de Mestrado/Dados/pu-points.csv',sep = ';', header=None, skiprows=[0])

cols_do = pd.read_csv('C:/Users/João Moura/Desktop/Tese de Mestrado/Dados/do-points.csv',sep = ';', nrows=0).columns.tolist()
df_do = pd.read_csv('C:/Users/João Moura/Desktop/Tese de Mestrado/Dados/do-points.csv',sep = ';', header=None, skiprows=[0])

cols_hub = pd.read_csv('C:/Users/João Moura/Desktop/Tese de Mestrado/Dados/hubs.csv',sep = ';', nrows=0).columns.tolist()
df_hub = pd.read_csv('C:/Users/João Moura/Desktop/Tese de Mestrado/Dados/hubs.csv',sep = ';', header=None, skiprows=[0])

objects = pd.read_csv('C:/Users/João Moura/Desktop/Tese de Mestrado/Dados/objects.csv',sep = ';', header=None, skiprows=[0])

objects = objects.rename(columns={0:"id", 1:"weight", 2:"volume"})
objects = objects.set_index('id')
#Extract time from columns 4 and 5
#date = datetime.fromisoformat('2022-10-19 09:09:13') 
#date.minute ; date.hour ; date.second ;
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
df_pu = df1_pu.join(df2_pu, how = 'outer')

df1_do = pd.DataFrame(do_id, columns=['id'])
df2_do = pd.DataFrame(do_tw, columns=['start_time_do', 'end_time_do'])
df_do = df1_do.join(df2_do, how = 'outer')

df_pu = df_pu.set_index('id')
df_do = df_do.set_index('id')

df_pu = df_pu.join(objects, how = 'outer') #Add objects to the pickup dataframe
