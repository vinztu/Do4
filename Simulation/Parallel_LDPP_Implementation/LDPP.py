import ray
import random

from Simulation.helper.pressure import compute_pressure
from Simulation.algorithms.LDPP_helper.ADMM.global_state import GlobalState as GlobalState_ADMM
from Simulation.algorithms.LDPP_helper.Greedy.global_state import GlobalState as GlobalState_Greedy
from Simulation.algorithms.LDPP_helper.agent import agent_computation

def import_global_state(sim):
    if "ADMM" in sim.algorithm:
        return GlobalState_ADMM
    elif "Greedy" in sim.algorithm:
        return GlobalState_Greedy

def LDPP(sim):
    
    # import the correct global state class
    GlobalState = import_global_state(sim)

    # serialization: cannot pickle 'cityflow.Engine' object
    # Due to serialization issues with ray, don't pass the cityflow.engine object into the ray.remote function
    args = {
        "algorithm": sim.algorithm,
        "lane_vehicle_count": sim.engine.get_lane_vehicle_count(),
        "intersections_data": sim.intersections_data,
        "lanes_data": sim.lanes_data,
        "params": sim.params,
        "phase_history": sim.params["phase_history"]
    }
        
    # create indices for intersections (randomely assigned each round)
    if "Greedy" in sim.algorithm:
        numbers = random.sample(range(1, len(sim.intersections_data) + 1), len(sim.intersections_data))  # Randomly shuffle the numbers list
        indices = {"indices": {item: numbers[i] for i, item in enumerate(sim.intersections_data)}}
        args.update(indices)
    
    # put it in the shared memory
    arguments_id = ray.put(args)
    
    # define a global state to "simulate communication" among neighbours
    global_state = GlobalState.remote(args)
    
    # to simplify (no extra communication for pressure values necessary) the implementation, we compute the pressure values first for all intersections "centralized"
    pressure_pp = {}
    for intersection in sim.intersections_data:
        _, pressure_pp[intersection] = compute_pressure(args, intersection)
        
    pressure_per_phase_id = ray.put(pressure_pp)

    # store all future results
    futures = []
    
    # Start a new process for each intersection
    for intersection in sim.intersections_data:
        # This remote call returns a future, a so-called Ray object reference
        futures.append(agent_computation.remote(global_state, intersection, arguments_id, pressure_per_phase_id))

    # Fetch futures with ray.get
    futures_completed = ray.get(futures)
    
    
    highest_phases = {}
    for intersection, pressure, objective, x_intersection in futures_completed:
        
        # update values for performance metrics
        # only take those pressures into account for which the phase got selected
        sim.perform["current_pressure"][intersection] = pressure[-1]
        sim.perform["current_objective"][intersection] = objective[-1]
        highest_phases[intersection] = x_intersection
        
        if "LDPP-T" in sim.algorithm:
            # update past decisions (delete last entry and add the latest phase)
            sim.params["phase_history"][intersection][1:] = sim.params["phase_history"][intersection][:-1]
            sim.params["phase_history"][intersection][0] = x_intersection
    
    return highest_phases
        
    
    