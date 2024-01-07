# Testing Distance Matrix computation with Google API
# Input: Latitude and Longitude
# Output: Distance Matrix


import googlemaps
import copy
from itertools import product

def calculate_distance_matrix(api_key, origins, destinations, mode="driving", avoid=None, units="metric"):
    """
    Calculate the distance matrix using Google Maps Distance Matrix API.

    Parameters:
    - api_key (str): Your Google Maps API key.
    - origins (list of tuples): List of (latitude, longitude) tuples representing the origin coordinates.
    - destinations (list of tuples): List of (latitude, longitude) tuples representing the destination coordinates.
    - mode (str): The mode of transportation (e.g., "driving", "walking", "bicycling", "transit").
    - avoid (list): List of route restrictions to avoid (e.g., ["tolls", "ferries"]).
    - units (str): Units for distance measurement ("metric" or "imperial").

    Returns:
    - distance_matrix (list of lists): The distance matrix, where distance_matrix[i][j] is the distance from origin i to destination j.
    """

    gmaps = googlemaps.Client(key=api_key)

    # Create Cartesian product of origins and destinations
    combinations = list(product(origins, destinations))

    # Extract latitudes and longitudes from the combinations
    origins_latlng = [coord for coord, _ in combinations]
    destinations_latlng = [coord for _, coord in combinations]

    # Convert coordinates to string format
    origins_str = ['{},{}'.format(lat, lng) for lat, lng in origins_latlng]
    destinations_str = ['{},{}'.format(lat, lng) for lat, lng in destinations_latlng]

    # Use the Distance Matrix API to get the distances
    result = gmaps.distance_matrix(
        origins=origins_str,
        destinations=destinations_str,
        mode=mode,
        avoid=avoid,
        units=units
    )

    # Extract distances from the result and build the distance matrix
    distance_matrix = [[element['distance']['value'] for element in row['elements']] for row in result['rows']]

    return distance_matrix

# Example usage:
api_key = "AIzaSyCPGZmyByzVU8rIoIxLeSBGw3hHPErFW20"

lat = list(points['latitude'])
long = list(points['longitude'])
n = len(lat)

origins = []

for i in range(3):
    origins.append((lat[i],long[i]))

destinations = copy.deepcopy(origins)

distance_matrix = calculate_distance_matrix(api_key, origins, destinations)

# Now distance_matrix contains the real distances between all pairs of points  