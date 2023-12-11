def load_parameters_common():

    # config file dir\n",
    dir_config_file = 'CityFlow/examples/test/config.json'

    # Common parameters for all algorithms
    dir_name = "first_try"
    filename = "try"

    # number of simulation rounds
    number_of_rounds = 2

    # Predefined phases
    phases = {0: [0, 7, 2, 3, 6, 10],
              1: [1, 8, 2, 3, 6, 10],
              2: [4, 11, 2, 3, 6, 10],
              3: [5, 9, 2, 3, 6, 10],
              4: [0, 1, 2, 3, 6, 10],
              5: [7, 8, 2, 3, 6, 10],
              6: [9, 11, 2, 3, 6, 10],
              7: [4, 5, 2, 3, 6, 10]
             }
    
    # define the number of movements
    movements = 12

    # tl-update interval
    delta = 20

    # idle time (idle time <= delta)
    idle_time = 5

    # simulation duration
    sim_duration = 1000

    # saturation flow rate
    saturation_flow = 2

    # for cityflow engine
    thread_num = 1
    

    common_params = {
        "dir_config_file": dir_config_file,
        "dir_name": dir_name,
        "filename": filename,
        "number_of_rounds": number_of_rounds,
        "phases": phases,
        "movements": movements,
        "delta": delta,
        "idle_time": idle_time,
        "sim_duration": sim_duration,
        "saturation_flow": saturation_flow, # could be made specific for each lane
        "thread_num": thread_num
    }
    
    return common_params


def load_parameters_MP():
    # Additional parameters specific to MP algorithm
    
    ### No additional parameters
    
    return {}


def load_parameters_CA_MP():
    # Additional parameters specific to CA_MP algorithm

    capacity = 30 # can load a json file in initialization.py with individual capacities
    c_inf = 35
    m = 2

    ca_mp_params = {
        "capacity": capacity,
        "c_inf": c_inf,
        "m": m
    }
    
    return ca_mp_params

def load_parameters_Centralized(common_params):
    # Additional parameters specific to Centralized algorithm
    
    capacity = 30                                                                             # can load a json file in initialization.py with individual capacities
    scaling = 10                                                                              # reduces the amount of variables by /scaling (SCALING <= DELTA)
    prediction_horizon = 2                                                                    # number of planning steps (actual horizon is * scaling)
    num_tl_updates = ((prediction_horizon * scaling) // common_params["delta"]) + 1           # number of tl updates within the prediction horizon time span
    exogenous_inflow = 0.1 * scaling                                                          # number of vehicles that enter from the outside per time step
    alpha = 0.5                                                                               # discount parameter
    
    
    centralized_params = {
        "capacity": capacity,
        "prediction_horizon": prediction_horizon,
        "num_tl_updates": num_tl_updates,
        "scaling": scaling,
        "exogenous_inflow": exogenous_inflow,
        "alpha": alpha
    }
    
    return centralized_params
    


def load_parameters(algorithm):
    common_params = load_parameters_common()
    
    if algorithm == "MP":
        mp_params = load_parameters_MP()
        common_params.update(mp_params)
    elif algorithm == "CA_MP":
        ca_mp_params = load_parameters_CA_MP()
        common_params.update(ca_mp_params)
    elif algorithm == "Centralized":
        centralized_params = load_parameters_Centralized(common_params)
        common_params.update(centralized_params)
    else:
        raise ValueError("Unsupported algorithm: {}".format(algorithm))
    
    return common_params



