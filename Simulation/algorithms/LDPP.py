import ray
import numpy as np

from Simulation.helper.pressure import compute_pressure
from Simulation.algorithms.LDPP_helper.ADMM.ADMM import ADMM
from Simulation.algorithms.LDPP_helper.Greedy.Greedy import Greedy


def LDPP(sim):

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
        
    pressure_per_phase_id = ray.put(pressure_pp)

    # Consensus
    if "ADMM" in sim.algorithm:
        x, objective, pressure = ADMM(sim, pressure_per_phase_id, arguments_id)
    elif "Greedy" in sim.algorithm:
        x, objective, pressure = Greedy(sim, pressure_per_phase_id, arguments_id)

    
    highest_phases = {}
    for intersection in sim.intersections_data:
        
        # update values for performance metrics
        # only take those pressures into account for which the phase got selected
        sim.perform["current_pressure"][intersection] = pressure[intersection][-1]
        sim.perform["current_objective"][intersection] = objective[intersection][-1]
        highest_phases[intersection] = np.argmax(x[intersection])
        
        if "LDPP-T" in sim.algorithm:
            # update past decisions (delete last entry and add the latest phase)
            sim.params["phase_history"][intersection][1:] = sim.params["phase_history"][intersection][:-1]
            sim.params["phase_history"][intersection][0] = np.argmax(x[intersection])
    
    return highest_phases
        
    
    