import ray
import numpy as np

from Simulation.algorithms.LDPP_helper.ADMM.initial_values import create_initial_values
from Simulation.algorithms.LDPP_helper.ADMM.waiting_neighbours import waiting_x_and_lambda_neighbours, waiting_z_g_neighbours
from Simulation.algorithms.LDPP_helper.objective_evaluation import obj_eval

from Simulation.algorithms.LDPP_helper.ADMM.min_z_binary import min_z as min_z_binary
from Simulation.algorithms.LDPP_helper.ADMM.min_z_continuous import min_z as min_z_continuous

from Simulation.algorithms.LDPP_helper.min_x_threshold import min_x as min_x_threshold
from Simulation.algorithms.LDPP_helper.min_x_green_flow import min_x as min_x_green_flow


def import_z_functions(arguments):
    if arguments["params"]["z_domain"] == "binary":
        return min_z_binary
    else:
        return min_z_continuous
        
def import_x_functions(arguments):
    if "LDPP-T" in arguments["algorithm"]:
        return min_x_threshold
    elif "LDPP-GF" in arguments["algorithm"]:
        return min_x_green_flow
    else:
        print(f'WRONG ALGORITHM {arguments["algorithm"]}')


def ADMM(global_state, intersection, arguments, pressure_per_phase, env):
    
    # import necessary functions
    min_z = import_z_functions(arguments)
    min_x = import_x_functions(arguments)
    
    # initialize x, lambda, z_g and write x and lambda_ to the global state
    x, lambda_, z_g = create_initial_values(arguments, intersection)
    ray.get(global_state.initialize_variables.remote(arguments, x, lambda_, z_g, intersection))
    
    # wait for neighbours to write their update z_g into the global dict
    z_g_neighbours = waiting_z_g_neighbours(arguments, 0, intersection, global_state)
    z_g.update(z_g_neighbours)
    
    # store all local objective values troughout the ADMM iterations
    pressure = []
    objective = []
    
    ## start ADMM algorithm
    for it in range(arguments["params"]["max_it"]):
    
        # compute objective and pressure values
        press, obj =  obj_eval(x, pressure_per_phase, arguments, intersection, it)
        pressure.append(press)
        objective.append(obj)
        
        # update x variables update the latest x_i variable in global state "Communication"
        x_agent, _, _ = min_x(pressure_per_phase, arguments, env, intersection, it, z_g = z_g, lambda_ = lambda_)
        x.update(x_agent)
        ray.get(global_state.set_x.remote(it + 1, intersection, x_agent[(it + 1, intersection)]))
    
        # we wait for the update of neighbours variables (x_i and lambda_)
        # as we need them in min_z
        # and update dict x and lambda_ to include neighbours decision variables
        x_neighbours, lambda_neighbours = waiting_x_and_lambda_neighbours(arguments, it + 1, intersection, global_state)
        x.update(x_neighbours)
        lambda_.update(lambda_neighbours)
    
        # update z variables (in case z is continuous --> lambda_ not needed here) and write it in global state
        z_g_agent = min_z(x, lambda_, arguments, env, intersection, it)
        z_g.update(z_g_agent)
        ray.get(global_state.set_z_g.remote(it + 1, intersection, z_g_agent))
        
        
        # wait for neighbours to write their update z_g into the global dict
        z_g_neighbours = waiting_z_g_neighbours(arguments, it + 1, intersection, global_state)
        z_g.update(z_g_neighbours)
    
        # update dual variables
        # update each element (for each neighbour) from the dual variable \lambda_i separately
        temp = {}
        for neighbour in arguments["intersections_data"][intersection]["neighbours"].union({intersection}):
            temp[neighbour] = lambda_[(it, intersection)][neighbour] + arguments["params"]["rho"] * (x[(it + 1, intersection)][neighbour] - z_g[(it + 1, neighbour)])
        
        lambda_agent = {(it + 1, intersection): temp}
        lambda_.update(lambda_agent)
            

        # if binary z chosen, update lambda in the global state
        # we don't have to wait here yet for other neighbours to write their lambda to the global state
        # as only our "own" lambda is needed in min_x
        if arguments["params"]["z_domain"] == "binary":
            ray.get(global_state.set_lambda_.remote(it + 1, intersection, lambda_agent[(it + 1, intersection)]))
    
    # update sim.performance and write back to highest_phases and return
    # optimal phase for intersection 
    x_intersection = np.argmax(x[(it, intersection)][intersection])
    
    return pressure, objective, x_intersection