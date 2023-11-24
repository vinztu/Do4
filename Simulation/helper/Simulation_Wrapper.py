from tqdm.notebook import tqdm
from Simulation.helper.simulation_step import sim_step

# import all algorithms
from Simulation.algorithms.Max_Pressure import Max_Pressure


def sim_wrapper(sim, metrics_recorder):
    """ Wraps the simulation and calls the respective algorithm
    Then advances the simulation for Delta time steps
    
    """
    
    # all available algorithms
    algorithms = {
        "MP": Max_Pressure,
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
        selected_algorithm(sim)
        
        # stop the simulation timer
        metrics_recorder.stop_timer()
        
        # advance the simulation by (Delta - idle_time) time steps
        # followed be the simulation of the idle time
        sim_step(sim, metrics_recorder, current_time)
        
        # update performance measure for every Delta time steps
        metrics_recorder.infrequent_update(sim, current_time)
        
        # update the progress bar
        tqdm_bar.update(sim.params["delta"])
    
    # close the progress bar
    tqdm_bar.close()