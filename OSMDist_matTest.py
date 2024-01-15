#OpenStreetMaps distance matrix

# import osmnx as ox
# import networkx as nx
# import pandas as pd

# # Function to calculate the distance matrix using OSM data
# def calculate_distance_matrix(locations, location_city):
#     # Create a graph from OSM data
#     G = ox.graph_from_place(location_city, network_type='drive')

#     # Get the nodes from the graph
#     nodes = ox.graph_to_gdfs(G, edges=False)

#     # Create a dictionary to store coordinates
#     coords = {node: (data['y'], data['x']) for node, data in nodes.iterrows()}

#     # Create a distance matrix using networkx
#     G = ox.nearest_nodes(G, X=locations['Longitude'], Y=locations['Latitude'])
#     print(G)
#     dist_matrix = nx.floyd_warshall_numpy(G, weight='length')

#     return dist_matrix, coords



# lat = list(points['latitude'])
# long = list(points['longitude'])
# n = len(lat)

# # Example usage
# locations_data = pd.DataFrame({
#     'Latitude': lat,  # Replace with your latitude values
#     'Longitude': long  # Replace with your longitude values
# })

# # Replace 'City, Country' with the location you are interested in
# location_name = 'Lisbon, Portugal'
# distance_matrix, coordinates = calculate_distance_matrix(locations_data, location_name)

# print("Distance Matrix:")
# print(distance_matrix)

# print("\nCoordinates:")
# print(coordinates)

import osmnx as ox
import networkx as nx
from datetime import timedelta


graph_area = ("Lisbon District")
# G = ox.graph_from_place(graph_area, network_type='drive')
# (For a better accuracy, create a graph with lot more nodes:)
G = ox.graph_from_place(graph_area, network_type='drive', simplify=False)

# OSM data are sometime incomplete so we use the speed module of osmnx to add missing edge speeds and travel times
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

# Save graph to disk if you want to reuse it
# ox.save_graphml(G, "Lisbon.graphml")
# Load the graph
#G = ox.load_graphml("Lisbon.graphml")

# Plot the graph
fig, ax = ox.plot_graph(G, figsize=(10, 10), node_size=0, edge_color='y', edge_linewidth=0.2)

lat = list(points['latitude'])
long = list(points['longitude'])
n = len(lat)
dist_mat1 = []
dist_mat = []

for i in range(n):
    origin_coordinates = (lat[i], long[i])
    for j in range(n):
        destination_coordinates = (lat[j], long[j])
        origin_node = ox.nearest_nodes(G, Y=origin_coordinates[0], X=origin_coordinates[1])
        destination_node = ox.nearest_nodes(G, Y=destination_coordinates[0], X=destination_coordinates[1])
        distance_in_meters = nx.shortest_path_length(G, origin_node, destination_node, weight='length')
        dist_mat1.append(distance_in_meters)
        print("distance in meters", distance_in_meters)
    dist_mat.append(dist_mat1)
        
        
# # Two pairs of (lat,lng) coordinates
# origin_coordinates = (40.70195053163349, -74.01123198479581)
# destination_coordinates = (40.87148739347057, -73.91517498611597)

# If you want to take an address (osmx will use Nominatim service for this)
# origin_coordinates = ox.geocode("2 Broad St, New York, NY 10005")

# # In the graph, get the nodes closest to the points
# origin_node = ox.nearest_nodes(G, Y=origin_coordinates[0], X=origin_coordinates[1])
# destination_node = ox.nearest_nodes(G, Y=destination_coordinates[0], X=destination_coordinates[1])

# Get the shortest route by distance
shortest_route_by_distance = ox.shortest_path(G, origin_node, destination_node, weight='length')

# Plot the shortest route by distance
fig, ax = ox.plot_graph_route(G, shortest_route_by_distance, route_color='y', route_linewidth=6, node_size=0)

# Get the shortest route by travel time
shortest_route_by_travel_time = ox.shortest_path(G, origin_node, destination_node, weight='travel_time')

# Plot the shortest route by travel time
fig, ax = ox.plot_graph_route(G, shortest_route_by_travel_time, route_color='y', route_linewidth=6, node_size=0)

# Plot the 2 routes
fig, ax = ox.plot_graph_routes(G, routes=[shortest_route_by_distance, shortest_route_by_travel_time], route_colors=['r', 'y'], route_linewidth=6, node_size=0)

# Get the travel time, in seconds
# Note here that we use "nx" (networkx), not "ox" (osmnx)
travel_time_in_seconds = nx.shortest_path_length(G, origin_node, destination_node, weight='travel_time')
print("travel time in seconds", travel_time_in_seconds)

#The travel time in "HOURS:MINUTES:SECONDS" format
travel_time_in_hours_minutes_seconds = str(timedelta(seconds=travel_time_in_seconds))
print("travel time in hours minutes seconds", travel_time_in_hours_minutes_seconds)

# Get the distance in meters
distance_in_meters = nx.shortest_path_length(G, origin_node, destination_node, weight='length')
print("distance in meters", distance_in_meters)
# Distance in kilometers
distance_in_kilometers = distance_in_meters / 1000
print("distance in kilometers", distance_in_kilometers)