import ray
import numpy as np

from ..helper.pressure import compute_pressure
from .LDPP_helper.ADMM.ADMM import ADMM
from .LDPP_helper.Greedy.Greedy import Greedy

from .LDPP_helper.global_objective_threshold import global_objective as global_objective_threshold
from .LDPP_helper.global_objective_green_flow import global_objective as global_objective_green_flow


def import_global_objective_function(sim):
    if "LDPP-T" in sim.algorithm:
        return global_objective_threshold
    elif "LDPP-GF" in sim.algorithm:
        return global_objective_green_flow
    else:
        print(f'WRONG ALGORITHM {sim.algorithm}')


def LDPP(sim, current_time, retrieve_ADMM_objective, global_objective):

    # import the correct function
    global_obj = import_global_objective_function(sim)
    
    # serialization: cannot pickle 'cityflow.Engine' object
    # Due to serialization issues with ray, don't pass the cityflow.engine object into the ray.remote function
    args = {
        "algorithm": sim.algorithm,
        "lane_vehicle_count": sim.engine.get_lane_vehicle_count(),
        "intersections_data": sim.intersections_data,
        "lanes_data": sim.lanes_data,
        "params": sim.params,
    }
    
    if "LDPP-T" in sim.algorithm:
        args.update({"phase_history": sim.params["phase_history"]})
    
    # put it in the shared memory
    arguments_id = ray.put(args)
    
    
    # to simplify (no extra communication for pressure values necessary) the implementation, we compute the pressure values first for all intersections "centralized"
    pressure_pp = {}
    for intersection in sim.intersections_data:
        _, pressure_pp[intersection] = compute_pressure(args, intersection)
    

    # Consensus
    if "ADMM" in sim.algorithm:
        x, objective, pressure = ADMM(sim, pressure_pp, arguments_id)
    elif "Greedy" in sim.algorithm:
        x, objective, pressure = Greedy(sim, pressure_pp, arguments_id)
        
    
    if current_time in retrieve_ADMM_objective:
        retrieve_ADMM_objective[current_time] = objective
        
        # compute the global objective to compare to consensus algorithm
        if sim.params["compare_global"]:
            global_objective[current_time] = global_obj(sim, pressure_pp, sim.engine.get_lane_vehicle_count())
            
    
    highest_phases = {}
    for intersection in sim.intersections_data:
        
        chosen_phase = np.argmax(x[intersection][intersection])
        assert pressure[intersection][-1] == pressure_pp[intersection][chosen_phase], f"wrong pressure gurobi for {intersection}: {pressure[intersection][-1]} (Gurobi) and pressure {pressure_pp[intersection][chosen_phase]}"
        
        # update values for performance metrics
        # only take those pressures into account for which the phase got selected
        sim.perform["current_pressure"][intersection] = pressure[intersection][-1]
        sim.perform["current_objective"][intersection] = objective[intersection][-1]
        highest_phases[intersection] = chosen_phase
        
        if "LDPP-T" in sim.algorithm:
            # update past decisions (delete last entry and add the latest phase)
            sim.params["phase_history"][intersection][1:] = sim.params["phase_history"][intersection][:-1]
            sim.params["phase_history"][intersection][0] = chosen_phase 
    
    return highest_phases