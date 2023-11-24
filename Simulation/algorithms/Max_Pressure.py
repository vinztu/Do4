import numpy as np
from Simulation.helper.Pressure import compute_pressure
from Simulation.helper.TL_Activation import activate_tl

def Max_Pressure(sim):
    """ Computes 1 iteration of the original MP algorithm
    
    Parameters
    -----------
    sim : Simulation
        Object of the Simulation Class
        
    """
    
    # compute all pressures
    _, pressure_per_phase = compute_pressure(sim)
        
    # select the highest phase per intersection
    highest_phases = {inter_id: np.argmax(pressures) for inter_id, pressures in pressure_per_phase.items()}
    
    
    # update values for performance metrics
    # only take those pressures into account for which the phase got selected
    for intersection in sim.intersections_data:
        sim.perform["current_pressure"][intersection] = pressure_per_phase[intersection][highest_phases[intersection]]
        sim.perform["current_objective"][intersection] = pressure_per_phase[intersection][highest_phases[intersection]]


    # activate the new traffic lights
    activate_tl(sim, highest_phases)
    