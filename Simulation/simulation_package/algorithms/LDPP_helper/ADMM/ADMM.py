import ray
from tqdm.auto import tqdm
import numpy as np

from .initial_values import create_initial_values
from .min_z_binary import min_z as min_z_binary
from .min_z_continuous import min_z as min_z_continuous
from ..min_x_green_flow import min_x as min_x_green_flow
from ..min_x_threshold import min_x as min_x_threshold
from ..evaluate_objective_threshold import evaluate_objective as evaluate_objective_threshold
from ..evaluate_objective_green_flow import evaluate_objective as evaluate_objective_green_flow


def is_notebook():
    try:
        shell = get_ipython().__class__.__name__
        if shell == 'ZMQInteractiveShell' or shell == 'TerminalInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        else:
            return False
    except NameError:
        return False 
    
def objective_evaluation(sim):
    if "LDPP-T" in sim.algorithm:
        return evaluate_objective_threshold
    elif "LDPP-GF" in sim.algorithm:
        return evaluate_objective_green_flow
    else:
        print(f'WRONG ALGORITHM {sim.algorithm}')
    
def import_z_function(sim):
    if sim.params["z_domain"] == "binary":
        return min_z_binary
    else:
        return min_z_continuous
        
def import_x_function(sim):
    if "LDPP-T" in sim.algorithm:
        return min_x_threshold
    elif "LDPP-GF" in sim.algorithm:
        return min_x_green_flow
    else:
        print(f'WRONG ALGORITHM {sim.algorithm}')


def ADMM(sim, pressure_pp, arguments_id):
    """ Implements the ADMM loop to solve for the optimal phases
    
    Parameters
    -----------
    sim : Simulation
        Object of the Simulation Class
    
    pressure_pre_phase_id : ray.object
        Stores the pressure per phase for each intersection
    
    arguments_id : ray.object
        Stores data from sim (copy), since ray cannot serialize citylow objects
    
    
    Returns
    -----------
    x : dict
        Keys are intersection id's and values are np.arrays (one hot vector) where the optimal phase is active (=1)
    
    objective : dict
        Keys are intersection id's and values are a list of the objective value throughout the ADMM iterations for each intersection
    
    pressure : dict
        Keys are intersection id's and values are a list of the pressure value throughout the ADMM iterations for each intersection
    
    """
    # check if script is running in a notebook
    is_noteb = is_notebook()
    
    # put it in the shared memory
    pressure_per_phase_id = ray.put(pressure_pp)
    
    # import necessary functions
    min_x = import_x_function(sim)
    min_z = import_z_function(sim)
    
    # initial values
    x, z, lambda_ = create_initial_values(sim)
    objective = {intersection: [] for intersection in sim.intersections_data}
    pressure = {intersection: [] for intersection in sim.intersections_data}
    
    # include initial objective
    if sim.params["compare_global"]:
        # import the correct function
        eval_obj = objective_evaluation(sim)
        
        for intersection in sim.intersections_data:
            objective[intersection].append(eval_obj(pressure_pp, sim, intersection, x))
            pressure[intersection].append(pressure_pp[intersection][np.argmax(x[intersection][intersection])])
    
    # use a bar to display the progress
    tqdm_bar = tqdm(desc="ADDM Iteration Step", leave=False, total = sim.params["max_it"])

    # Iterate until max_it is reached
    for tau in range(sim.params["max_it"]):
                
            ###### MIN X ######
            # store all future results
            futures = []
            
            # Parallel maximization of min_x function
            for intersection in sim.intersections_data:
                # This remote call returns a future, a so-called Ray object reference
                futures.append(min_x.remote(pressure_per_phase_id, arguments_id, intersection, z, lambda_))
    
            # Fetch futures with ray.get and write it in a dict
            min_x_results = ray.get(futures)
    
            for intersection, x_optimized, obj_val, pressure_val in min_x_results:
                x[intersection] = x_optimized
                objective[intersection].append(obj_val)
                pressure[intersection].append(pressure_val)
            
            
            
            ###### MIN Z ######
            # Parallel maximization of compute parallel min z
            futures = []

            for intersection in sim.intersections_data:
                # This remote call returns a future, a so-called Ray object reference
                futures.append(min_z.remote(arguments_id, intersection, x, lambda_))
    
            # Fetch futures with ray.get and write it in a dict
            min_z_results = ray.get(futures)
            
            for intersection, z_optimized in min_z_results:
                z[intersection] = z_optimized
                
            
            ###### DUAL VARIABLE ######
            for intersection in sim.intersections_data:
                for neighbour in sim.intersections_data[intersection]["neighbours"].union({intersection}):
                    
                    # the bracket is a difference of two numpy arrays containing phases
                    lambda_[intersection][neighbour] += sim.params["rho"] * (x[intersection][neighbour] - z[neighbour])
                    
                    
                    
            ###### Check the termination condition ######
            if tau >= 5:
                
                # sum up objective over each intersection
                total_objective = list(map(sum, zip(*objective.values())))

                # Calculate the moving average of the last 3 values (t, t-1, t-2)
                current_moving_average = sum(total_objective[-3:]) / 3
                
                # define the threshold to be 1% of the objective value
                threshold = abs(total_objective[-1]) * 0.01
            
                previous_moving_average = sum(total_objective[-4:-1]) / 3  # Moving average of the last 3 iterations (t-1, t-2, t-3)
                
                if abs(previous_moving_average - current_moving_average) < threshold:
                    break
            
            # update the progress bar
            tqdm_bar.update(1)
            
    
    # close the progress bar
    if is_noteb:
        tqdm_bar.container.close()
    else:
        tqdm_bar.close()
    
    # save the number of ADMM-iterations rounds
    sim.params["num_consensus_iterations"].append(tau + 1) # plus 1, since tau starts at 0
    
    # record the ray timeline to analyse the behaviour
    #ray.timeline(filename="ray_timeline_ADMM.json")
    
    return x, objective, pressure