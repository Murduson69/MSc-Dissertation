import math
from itertools import permutations

def calculate_distance(point1, point2):
    """Calculates Euclidean distance between two points (X, Y)."""
    return math.sqrt((point2['X'] - point1['X'])**2 + (point2['Y'] - point1['Y'])**2)

def calculate_travel_time_min(distance_km, speed_m_s):
    """Converts speed to km/h and returns travel time in minutes."""
    speed_km_h = speed_m_s * 3.6
    return (distance_km / speed_km_h) * 60

def find_optimal_route(target_wts, base_coords, ts, ti, vs):
    """
    Finds the shortest TSP (Traveling Salesperson Problem) route for the target WTs and calculates total shift time.
    """
    shortest_route = None
    min_distance = float('inf')
    
    # Generate all possible visiting orders
    for route_permutation in permutations(target_wts):
        current_distance = 0
        current_point = base_coords
        
        # Base -> WT1 -> WT2 ...
        for wt in route_permutation:
            current_distance += calculate_distance(current_point, wt)
            current_point = wt
            
        # Last WT -> Base
        current_distance += calculate_distance(current_point, base_coords)
        
        # Keep the shortest
        if current_distance < min_distance:
            min_distance = current_distance
            shortest_route = route_permutation

    # Calculate required time for this optimal route
    travel_time = calculate_travel_time_min(min_distance, vs)
    working_time = len(shortest_route) * (ts + (2 * ti))
    
    total_time_hours = (travel_time + working_time) / 60
    
    return shortest_route, min_distance, total_time_hours