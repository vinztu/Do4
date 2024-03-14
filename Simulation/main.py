from simulation_package.helper.Simulation_class import Simulation
from simulation_package.helper.initialization import initialize
from simulation_package.helper.simulation_wrapper import sim_wrapper
from simulation_package.parameter_loader import load_parameters
from simulation_package.helper.fake_ray_agents import fake_agent
from simulation_package.metrics import Metrics


def main(algorithm, road_network, write_phase_to_json, load_capacities, ext_dict, retrieve_ADMM_objective, global_objective):
    
    if algorithm != "Centralized":
        import ray
    
    # load simulation parameters
    params = load_parameters(algorithm, road_network, ext_dict)

    # instantiate the sim object
    sim = Simulation(params, algorithm, write_phase_to_json)

    # read (write) the necessary from (to) the roadnet file
    initialize(sim, load_capacities)
    
    if algorithm != "Centralized":
        # do some fake computations to warmup ray (consistent computation time)
        fake_agent(sim)

    # do many rounds of the same simulation
    for current_round in range(sim.params["number_of_rounds"]):

        # instantiate the Metrics class
        metrics_recorder = Metrics(sim)

        # start the simulation
        sim_wrapper(sim, metrics_recorder, retrieve_ADMM_objective, global_objective)

        # generate the performance report
        metrics_recorder.generate_report(sim, current_round)
        
        # reset variables for the next round
        if current_round < sim.params["number_of_rounds"] - 1:
            sim.reset_variables(current_round)
    

    if algorithm != "Centralized":
        # terminate ray runtime
        ray.shutdown()

    print("\n\n##### SIMULATION COMPLETED #####")
    
##########################################################################################
##########################################################################################
import numpy as np
from itertools import product
import json

delta_and_idle = [(20, 0)]
# small between 12 - 15 cars per lane
#capacity = [13, 25]
#V1 = [0, 1, 3]
#V2 = [0, 1, 3]
#V3 = [0, 1, 3]
#L = [5, 20]
#rho = [0.5, 2]


# used algorithm
# Fixed-Time, MP, CA_MP, Centralized, LDPP + T/GF + ADMM/Greedy
algorithm = "LDPP-T-ADMM"

# Specify which road network to use (dir name)
road_network = "3_4_Fine"

# write phase definitions back to roadnet file
write_phase_to_json = True if road_network != "Manhattan" else False

# use custom .json file with capacities
load_capacities = False if road_network != "Manhattan" else True

# Generate all possible combinations of parameter values
parameter_combinations = product(delta_and_idle)#, capacity, V1, V2, V3, L, rho)


retrieve_ADMM_objective = {40: None, 60: None, 100: None, 200: None, 500: None, 1000: None, 1500: None, 2000: None}
global_objective = {}


for i, combination in enumerate(parameter_combinations):
        
    ext_dict = {
        "delta": combination[0][0],
        "idle_time": combination[0][1],
        #"capacity": combination[1],
        #"V1": combination[2],
        #"V2": combination[3],
        #"V3": combination[4],
        #"L": combination[5],
        #"rho": combination[6]
    }
    
    print(ext_dict)
    main(algorithm, road_network, write_phase_to_json, load_capacities, ext_dict, retrieve_ADMM_objective, global_objective)

    if "LDPP" in algorithm:
        # Save the dictionary to a JSON file
        combined_dict = {"retrieve_ADMM_objective": retrieve_ADMM_objective, "global_objective": global_objective}

        # Save to a JSON file
        with open(f'OBJECTIVE_{algorithm.split("-")[1]}_{algorithm.split("-")[2]}_{i}.json', 'w') as json_file:
            json.dump(combined_dict, json_file, indent=2)