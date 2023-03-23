
import time

import numpy as np
from osmnx import graph_from_place, config

from route_optimization import SARouteOptimizer, SAModel
from utils import calculate_distance_matrix, create_map, calculate_full_path, create_init_route


class Model(SAModel):

    def __init__(self, cost_matrix):
        self.cost_matrix = cost_matrix

    def cost(self, route):
        cost = 0
        for i in range(len(route) - 1):
            from_index = route[i]
            to_index = route[i + 1]
            cost += self.cost_matrix[from_index][to_index]
        return cost

#всегда false 1 арг
#
def main(USE_SAVED_DISTANCES,coordinate,START_HILL,END_HILL):
    config(log_console=True, use_cache=True, cache_folder='./cache')



    print("Calculating graph")
    graph = graph_from_place('Moscow', network_type='walk')

    hill_names, coordinates = [], []
    for a, b in coordinate.items():
        hill_names.append(a)
        coordinates.append(b)
    print(hill_names, coordinates)
    print([START_HILL, END_HILL])
    distances_matrix = None
    if USE_SAVED_DISTANCES:
        print("Loading distances from file")
        try:
            distances_matrix = np.loadtxt("distances.txt")
        except OSError:
            USE_SAVED_DISTANCES = False
            print("Could not find distances.txt file.")

    if not USE_SAVED_DISTANCES:
        print("Calculating distances between points")
        distances_matrix = calculate_distance_matrix(graph, coordinates)
        print("Saving distances to file")
        np.savetxt("distances.txt", distances_matrix)

    optimizer = SARouteOptimizer(model=Model(cost_matrix=distances_matrix),
                                 max_iter=1000,
                                 max_iter_without_improvement=300)

    print("Calculating optimal order of hills")
    init_route = create_init_route(hill_names.index(START_HILL), hill_names.index(END_HILL), distances_matrix.shape[0])
    start_time = time.time()
    optimal_route, total_distance = optimizer.run(init_route)
    end_time = time.time()
    duration_ms = 1000 * (end_time - start_time)
    print(f"Solution took {duration_ms:0.0f} ms")


    print("Creating optimal path")
    full_path, distances = calculate_full_path(graph, optimal_route, coordinates)

    print("Creating map")
    map = create_map(graph, full_path, optimal_route, hill_names, coordinates, distances)
    print("Saving map to file")
    map.save('results/optimal_route.html')

