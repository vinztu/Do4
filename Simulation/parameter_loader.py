def load_parameters_common():

    # for cityflow engine
    thread_num = 1
    
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

    # capacity of a lane (can load a json file in initialization.py with individual capacities)
    capacity = 30
    

    common_params = {
        "thread_num": thread_num,
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
        "capacity": capacity
    }
    
    return common_params


def load_parameters_MP():
    # Additional parameters specific to MP algorithm
    
    ### No additional parameters
    
    return {}


def load_parameters_CA_MP():
    # Additional parameters specific to CA_MP algorithm

    c_inf = 35
    m = 2

    ca_mp_params = {
        "c_inf": c_inf,
        "m": m
    }
    
    return ca_mp_params

def load_parameters_Centralized(common_params):
    # Additional parameters specific to Centralized algorithm
    
    # reduces the amount of variables by /scaling (SCALING <= DELTA)
    scaling = 10
    
    # number of planning steps (actual horizon is * scaling)
    prediction_horizon = 2
    
    # number of tl updates within the prediction horizon time span
    num_tl_updates = ((prediction_horizon * scaling) // common_params["delta"]) + 1
    
    # number of vehicles that enter from the outside per time step
    exogenous_inflow = 0.1 * scaling
    
    # discount parameter
    alpha = 0.5                                                                               
    
    
    centralized_params = {
        "prediction_horizon": prediction_horizon,
        "num_tl_updates": num_tl_updates,
        "scaling": scaling,
        "exogenous_inflow": exogenous_inflow,
        "alpha": alpha
    }
    
    return centralized_params
    

def load_parameters_LDPP():
    # Additional parameters specific to Centralized algorithm
    
    # maximal number of iterations for the ADMM algorithm
    max_it = 20
    
    # lagrangian parameter rho
    rho = 1
    
    # choose which penalty function to apply ("binary" or "continuous")
    penalty_function = "binary"
    
    # determine domain for z ("binary" or "continuous") --> affects z-update
    z_domain = "binary"
    
    lane_weight = "Constant"
    
    L = 10
    V = 2
    V1 = 2
    V2 = 3
    V3 = 1
    
    
    # Tune in Simulation_class.py
    #constant_weight 
    
    LDPP_params = {
        "max_it": max_it,
        "rho": rho,
        "penalty_function": penalty_function,
        "z_domain": z_domain,
        "lane_weight": lane_weight,
        "L": L,
        "V1": V1,
        "V2": V2,
        "V3": V3,
        "V": V
    }
    
    return LDPP_params
    
    

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
    elif algorithm == "LDPP":
        centralized_params = load_parameters_LDPP()
        common_params.update(centralized_params)
    else:
        raise ValueError("Unsupported algorithm: {}".format(algorithm))
    
    return common_params



