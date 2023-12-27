# add the root to sys.path
import sys
sys.path.append('/Users/vinz/Documents/ETH/Do4')

from Simulation.helper.Simulation_class import Simulation
from Simulation.helper.initialization import initialize
from Simulation.helper.simulation_wrapper import sim_wrapper
from Simulation.parameter_loader import load_parameters
from Simulation.metrics import Metrics


# used algorithm
# MP, CA_MP, Centralized
algorithm = "LDPP-T-Greedy"

if algorithm != "Centralized":
    import ray

# load simulation parameters
params = load_parameters(algorithm)

# instantiate the sim object
sim = Simulation(params, algorithm)

# read (write) the necessary from (to) the roadnet file
initialize(sim)

# do many rounds of the same simulation
for current_round in range(sim.params["number_of_rounds"]):

    # instantiate the Metrics class
    metrics_recorder = Metrics(sim)

    # start the simulation
    sim_wrapper(sim, metrics_recorder)

    # generate the performance report
    metrics_recorder.generate_report(sim, current_round)


if algorithm != "Centralized":
    # terminate ray runtime
    ray.shutdown()

print("\n\n##### SIMULATION COMPLETED #####")