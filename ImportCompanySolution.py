#Import the company results into a proper solution

import csv
import pandas as pd

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
    hubdados = '/hubs_aug.csv'
elif entry_data == 1:
    dados = 'Dados2'
    hubdados = '/hubs.csv'

cols_courier = pd.read_csv('C:/Users/'+path+'/Desktop/Tese de Mestrado/'+dados+'/couriers.csv',sep = ';', nrows=0).columns.tolist()
df_courier = pd.read_csv('C:/Users/'+path+'/Desktop/Tese de Mestrado/'+dados+'/couriers.csv',sep = ';', header=None, skiprows=[0])

df_courier = df_courier.set_index(0)

cols_csol = pd.read_csv('C:/Users/'+path+'/Desktop/Tese de Mestrado/'+dados+'/veículos_pedidos_pudo_rotas_20221215.csv',sep = ';', nrows=0).columns.tolist()
df_csol = pd.read_csv('C:/Users/'+path+'/Desktop/Tese de Mestrado/'+dados+'/veículos_pedidos_pudo_rotas_20221215.csv',sep = ';', header=None, skiprows=[0])

couriers = df_csol[0].unique().tolist()
# Create an empty dictionary
courier_hubs = {}
courier_veh = {}

for courier in couriers:  
    # Add key-value pairs to the dictionary
    courier_hubs[courier] = df_courier.loc[courier][5]
    courier_veh[courier] = df_courier.loc[courier][4]
    
hubs = set(courier_hubs.values())

company_sol = []
route = []

courier_num = 0
cour_sol = []

for i in range(len(df_csol)):
    if df_csol.iloc[i][0] != courier_num:
        if i != 0:
            route.append(courier_hubs[df_csol.iloc[i-1][0]])
            company_sol.append(route)
        route = []
        cour_sol.append(courier_veh[df_csol.iloc[i][0]])
        route.append(courier_hubs[df_csol.iloc[i][0]])
        courier_num = df_csol.iloc[i][0]
    route.append(df_csol.iloc[i][1])        
route.append(courier_hubs[df_csol.iloc[i-1][0]])
company_sol.append(route)  

comp_sol = []

for hub in hubs:
    hub_route = []
    for i in range(len(company_sol)):
        if company_sol[i][0] == hub:
            hub_route.append(company_sol[i])
    comp_sol.append(hub_route)
    
comp_veh_sol = [[2,2,2,2,2,2,2,2],[2,2,1,2,2,2,2,1,2,2,2,2,2,2]]
# RepairOps.solution_cost(comp_sol, dist_mat, points2, inv_points2, data, fleet, comp_veh_sol)
