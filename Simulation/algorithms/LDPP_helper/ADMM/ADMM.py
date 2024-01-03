import ray
from tqdm.auto import tqdm

from Simulation.algorithms.LDPP_helper.ADMM.initial_values import create_initial_values
from Simulation.algorithms.LDPP_helper.ADMM.min_z_binary import min_z as min_z_binary
from Simulation.algorithms.LDPP_helper.ADMM.min_z_continuous import min_z as min_z_continuous
from Simulation.algorithms.LDPP_helper.min_x_green_flow import min_x as min_x_green_flow
from Simulation.algorithms.LDPP_helper.min_x_threshold import min_x as min_x_threshold

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


def ADMM(sim, pressure_per_phase_id, arguments_id):
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
    
    # import necessary functions
    min_x = import_x_function(sim)
    min_z = import_z_function(sim)

    # initial values
    x, z, lambda_ = create_initial_values(sim)
    objective = {intersection: [] for intersection in sim.intersections_data}
    pressure = {intersection: [] for intersection in sim.intersections_data}


    # Iterate until max_it is reached
    for _ in tqdm(range(sim.params["max_it"]), desc="ADDM Iteration Step", leave=False):
        
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
                for neighbour in sim.intersections_data[intersection]["neighbours"]:
                    
                    # the bracket is a difference of two numpy arrays containing phases
                    lambda_[intersection][neighbour] += sim.params["rho"] * (x[intersection][neighbour] - z[neighbour])


    return x, objective, pressure