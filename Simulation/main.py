# add the root to sys.path
import sys
sys.path.append('/Users/vinz/Documents/ETH/Do4')

from Simulation.helper.Simulation_class import Simulation
from Simulation.helper.initialization import initialize
from Simulation.helper.simulation_wrapper import sim_wrapper
from Simulation.parameter_loader import load_parameters
from Simulation.helper.fake_ray_agents import fake_agent
from Simulation.metrics import Metrics


def main(algorithm, road_network, write_phase_to_json, load_capacities, ext_dict):
    
    if algorithm != "Centralized":
        import ray

    # load simulation parameters
    params = load_parameters(algorithm, road_network, ext_dict)

    # instantiate the sim object
    sim = Simulation(params, algorithm, sys_path, write_phase_to_json)

    # read (write) the necessary from (to) the roadnet file
    initialize(sim, load_capacities)
    
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


delta_and_idle = [(20, 0)]
# small between 12 - 15 cars per lane
capacity = [10]
V1 = [0, 1, 5]
V2 = [0, 1, 5]
V3 = [0, 1, 5]
L = [5, 20]
rho = [0.2, 1]


# used algorithm
# MP, CA_MP, Centralized, LDPP + T/GF + ADMM/Greedy
algorithm = "LDPP-T-Greedy"

# Specify which road network to use (dir name)
road_network = "3_4_Fine"

# write phase definitions back to roadnet file
write_phase_to_json = False

# use custom .json file with capacities
load_capacities = False

# Generate all possible combinations of parameter values
parameter_combinations = product(delta_and_idle)

for i, combination in enumerate(parameter_combinations):
    
    ext_dict = {
        "delta": combination[0][0],
        "idle_time": combination[0][1],
        "alpha": combination[1],
        "scaling": combination[2],
        "prediction_horizon": combination[3],
        #"V3": combination[4],
        #"L": combination[5],
        #"rho": combination[6]
    }
    print(ext_dict)
    
    main(algorithm, road_network, write_phase_to_json, load_capacities, ext_dict)