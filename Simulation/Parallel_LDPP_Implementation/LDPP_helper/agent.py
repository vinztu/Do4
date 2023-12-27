import ray
import gurobipy as gp
from gurobipy import GRB


from Simulation.algorithms.LDPP_helper.ADMM.ADMM import ADMM
from Simulation.algorithms.LDPP_helper.Greedy.Greedy import Greedy

        
@ray.remote
def agent_computation(global_state, intersection, arguments, pressure_per_phase):
     
    # define gurobi environment and set gurobi environment output to 0
    env = gp.Env(empty=True)
    env.setParam("OutputFlag",0)
    env.start()
    
    # differentiate between ADMM and Greedy
    if "ADMM" in arguments["algorithm"]:
        pressure, objective, x_intersection = ADMM(global_state, intersection, arguments, pressure_per_phase, env)
    
    elif "Greedy" in arguments["algorithm"]:
        pressure, objective, x_intersection = Greedy(global_state, intersection, arguments, pressure_per_phase, env)
    
    else:
        print(f'WRONG CONSENSUS ALGORITHM {arguments["algorithm"].split("-")[-1]}')
    
    return intersection, pressure, objective, x_intersection