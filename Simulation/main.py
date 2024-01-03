# add the root to sys.path
import sys
sys.path.append('/Users/vinz/Documents/ETH/Do4')

from Simulation.helper.Simulation_class import Simulation
from Simulation.helper.initialization import initialize
from Simulation.helper.simulation_wrapper import sim_wrapper
from Simulation.parameter_loader import load_parameters
from Simulation.metrics import Metrics


def main(algorithm, road_network, ext_dict):
    
    if algorithm != "Centralized":
        import ray

    # load simulation parameters
    params = load_parameters(algorithm, road_network, ext_dict)

    # instantiate the sim object
    sim = Simulation(params, algorithm)

    # read (write) the necessary from (to) the roadnet file
    initialize(sim)
    
    # do some fake computations to warmup ray (consistent computation time)
    fake_agent()

    # do many rounds of the same simulation
    for current_round in range(sim.params["number_of_rounds"]):

        # instantiate the Metrics class
        metrics_recorder = Metrics(sim)

        # start the simulation
        sim_wrapper(sim, metrics_recorder)

        # generate the performance report
        metrics_recorder.generate_report(sim, current_round)
        
        # reset variables for the next round
        sim.reset_variables()


    if algorithm != "Centralized":
        # terminate ray runtime
        ray.shutdown()

    print("\n\n##### SIMULATION COMPLETED #####")
    
##########################################################################################
##########################################################################################
import numpy as np
from itertools import product

delta_and_idle = [(1, 1), (10, 2), (20, 5)]
delta_and_idle = [(20, 5)]

# used algorithm
# MP, CA_MP, Centralized, LDPP + T/GF + ADMM/Greedy
algorithm = "LDPP-T-Greedy"

# Specify which road network to use (dir name)
road_network = "3_4_Fine"

# Generate all possible combinations of parameter values
parameter_combinations = product(delta_and_idle)

for combination in parameter_combinations:
    ext_dict = {
        "delta": combination[0][0],
        "idle_time": combination[0][1],
    }
    main(algorithm, road_network, ext_dict)