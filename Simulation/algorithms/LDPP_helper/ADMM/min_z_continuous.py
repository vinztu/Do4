import numpy as np
import ray

@ray.remote
def min_z(arguments, agent_intersection, x, lambda_):
    """
    Solve min z problem to get only the optimal for z_g
    
    lambda_ not needed
    """
    
    # a list with all neghbouring intersections
    neighbouring_intersections = arguments["intersections_data"][agent_intersection]["neighbours"].union({agent_intersection})
    
    
    # define an empty array, where the neighbours decision will be stored
    sum_decisions = np.zeros(len(arguments["params"]["phases"]))
    
    
    # instead of interating over all M(i,j) = g, we iterate over all neighbours,
    # since each neighbour holds 1 entry, such that M(i,j) = g
    for neighbour in neighbouring_intersections:
        
        sum_decisions += x[neighbour][agent_intersection]
        
    
    # divide by the number of neighbours
    z_optimized = sum_decisions / len(neighbouring_intersections)
    
    
    return agent_intersection, z_optimized
        
    