# -*- coding: utf-8 -*-
"""
Created on Sat Oct 28 16:17:55 2023

@author: João Moura
"""

import csv

cols_vehtypes = pd.read_csv('C:/Users/'+path+'/Desktop/Tese de Mestrado/'+dados+'/vehicle_types.csv',sep = ';', nrows=0).columns.tolist()
df_vehtypes = pd.read_csv('C:/Users/'+path+'/Desktop/Tese de Mestrado/'+dados+'/vehicle_types.csv',sep = ';', header=None, skiprows=[0])
