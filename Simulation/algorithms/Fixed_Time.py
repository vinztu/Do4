import numpy as np
import ray
from Simulation.helper.pressure import compute_pressure

def Fixed_Time(sim):
    """ Fixed Time controller
    
    Calculates the pressure anyway as a metric (not for control purposes)
    
    Parameters
    -----------
    sim : Simulation
        Object of the Simulation Class
        
    """
    
    futures = []

    # serialization: cannot pickle 'cityflow.Engine' object
    # Due to serialization issues with ray, don't pass the cityflow.engine object into the ray.remote function
    arguments = ray.put({
        "lane_vehicle_count": sim.engine.get_lane_vehicle_count(),
        "intersections_data": sim.intersections_data,
        "lanes_data": sim.lanes_data,
        "params": sim.params
    })
    
    # find next active phase
    index_prev_phase = sim.phase_sequence.index(sim.params["previous_phase"])
    next_phase = sim.phase_sequence[(index_prev_phase + 1) % len(sim.phase_sequence)]
    
    # update the previous phase
    sim.params["previous_phase"] = next_phase

        
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
        
        highest_phases[intersection] = next_phase
    
    return highest_phases


@ray.remote
def agent_computation(arguments, intersection):

    # compute all pressures per intersection
    _, pressure_per_phase = compute_pressure(arguments, intersection)

    return intersection, pressure
    