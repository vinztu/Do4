import ray
from Simulation.helper.pressure import compute_pressure
from algorithms.LDPP_helper.global_state import GlobalState
from algorithms.LDPP_helper.agent import agent_computation

def LDPP(sim):

    # serialization: cannot pickle 'cityflow.Engine' object
    # Due to serialization issues with ray, don't pass the cityflow.engine object into the ray.remote function
    arguments = {
        "lane_vehicle_count": sim.engine.get_lane_vehicle_count(),
        "intersections_data": sim.intersections_data,
        "lanes_data": sim.lanes_data,
        "params": sim.params,
        "phase_history": sim.params["phase_history"]
    }
    
    arguments_id = ray.put(arguments)
    
    # define a global state to "simulate communication" among neighbours
    global_state = GlobalState.remote(arguments)
    
    # to simplify (no extra communication for pressure values necessary) the implementation, we compute the pressure values first for all intersections "centralized"
    pressure_per_phase = {}
    for intersection in sim.intersections_data:
        _, pressure_per_phase[intersection] = compute_pressure(arguments, intersection)
        
    pressure_per_phase_id = ray.put(pressure_per_phase)

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
        
        # update past decisions (delete last entry and add the latest phase)
        sim.params["phase_history"][intersection][1:] = sim.params["phase_history"][intersection][:-1]
        sim.params["phase_history"][intersection][0] = x_intersection
    
    return highest_phases
        
    
    