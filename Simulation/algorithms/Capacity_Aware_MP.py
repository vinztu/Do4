import numpy as np
import ray
from Simulation.helper.pressure_normalized import compute_normalized_pressure

def Capacity_Aware_MP(sim):
    """ Computes 1 iteration of the Capacity Aware MP algorithm
    
    Parameters
    -----------
    sim : Simulation
        Object of the Simulation Class
        
    """
    
    futures = []

    # serialization: cannot pickle 'cityflow.Engine' object
    # Due to serialization issues with ray, don't pass the cityflow.engine object into the ray.remote function
    arguments = {
        "lane_vehicle_count": sim.engine.get_lane_vehicle_count(),
        "intersections_data": sim.intersections_data,
        "lanes_data": sim.lanes_data,
        "params": sim.params
    }

    # Start a new process for each intersection
    for intersection in sim.intersections_data:
        
        #This remote call returns a future, a so-called Ray object reference
        futures.append(agent_computation.remote(arguments, intersection))
    
    
    # Fetch futures with ray.get
    futures_completed = ray.get(futures)

    highest_phases = {}
    # update values for performance metrics
    # only take those pressures into account for which the phase got selected
    for intersection, pressure, opt_phase in futures_completed:
        sim.perform["current_pressure"][intersection] = pressure
        sim.perform["current_objective"][intersection] = pressure
        highest_phases[intersection] = opt_phase

        
    return highest_phases


@ray.remote
def agent_computation(arguments, intersection):

    # compute all pressures per intersection
    _, pressure_per_phase = compute_normalized_pressure(arguments, intersection)

    # select the highest phase per intersection
    highest_phase = np.argmax(pressure_per_phase)

    # corresponding pressure
    pressure = pressure_per_phase[highest_phase]

    return intersection, pressure, highest_phase