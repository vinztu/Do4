import ray

from Simulation.algorithms.LDPP_helper.min_x_green_flow import min_x as min_x_green_flow
from Simulation.algorithms.LDPP_helper.min_x_threshold import min_x as min_x_threshold


def import_x_function(sim):
    if "LDPP-T" in sim.algorithm:
        return min_x_threshold
    elif "LDPP-GF" in sim.algorithm:
        return min_x_green_flow
    else:
        print(f'WRONG ALGORITHM {sim.algorithm}')
        
        
def optimize_objective(sim, pressure_per_phase_id, arguments_id, DET, optimal_phases, objective, pressure):
    
    # import necessary functions
    min_x = import_x_function(sim)
    
    # store all future results
    futures = []

    # Parallel maximization of min_x function
    for intersection in sim.intersections_data:
        if DET[intersection] == False:
            # This remote call returns a future, a so-called Ray object reference
            futures.append(min_x.remote(pressure_per_phase_id, arguments_id, intersection, DET = DET, optimal_phases = optimal_phases))

    # Fetch futures with ray.get and write it in a dict
    min_x_results = ray.get(futures)

    for intersection, x_optimized, obj_val, pressure_val in min_x_results:
        optimal_phases[intersection] = x_optimized
        objective[intersection].append(obj_val)
        pressure[intersection].append(pressure_val)