from tqdm.auto import tqdm
from .simulation_step import sim_step
from .tl_activation import activate_tl

# import all algorithms
from ..algorithms.Fixed_Time import Fixed_Time
from ..algorithms.Max_Pressure import Max_Pressure
from ..algorithms.Capacity_Aware_MP import Capacity_Aware_MP
from ..algorithms.Centralized import Centralized_MP
from ..algorithms.LDPP import LDPP


def sim_wrapper(sim, metrics_recorder, retrieve_ADMM_objective, global_objective):
    """ Wraps the simulation and calls the respective algorithm
    Then advances the simulation for Delta time steps
    
    """
    
    # all available algorithms
    algorithms = {
        "Fixed-Time": Fixed_Time,
        "MP": Max_Pressure,
        "CA_MP": Capacity_Aware_MP,
        "Centralized": Centralized_MP,
        "LDPP-T-ADMM": LDPP,
        "LDPP-GF-ADMM": LDPP,
        "LDPP-T-Greedy": LDPP,
        "LDPP-GF-Greedy": LDPP
    }

    # select the chosen algorithm
    selected_algorithm = algorithms.get(sim.algorithm)
    
    if selected_algorithm is None:
        raise ValueError("This algorithm is not implemented")

    # use a bar to display the progress
    tqdm_bar = tqdm(desc="Simulation Time Step", total = sim.params["sim_duration"])
    
    # Start the simulation and conduct 
    for current_time in range(0, sim.params["sim_duration"], sim.params["delta"]):
        
        # start the simulation timer
        metrics_recorder.start_timer()

        # call the algorithm to update the tl
        if "LDPP" in sim.algorithm:
            optimal_phases = selected_algorithm(sim, current_time, retrieve_ADMM_objective, global_objective)
        else:
            optimal_phases = selected_algorithm(sim)

        # stop the simulation timer
        metrics_recorder.stop_timer()

        # activate the new traffic lights
        activate_tl(sim, optimal_phases)
            
        # advance the simulation by (Delta - idle_time) time steps
        # followed be the simulation of the idle time
        sim_step(sim, metrics_recorder, current_time)
            
        # update performance measure for every Delta time steps
        metrics_recorder.infrequent_update(sim, current_time)
        
        # update the progress bar
        tqdm_bar.update(sim.params["delta"])
            
    # close the progress bar
    tqdm_bar.close()
