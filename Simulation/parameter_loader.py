from Simulation.helper.phase_definitions import phase_definitions

def load_parameters_common(road_network, ext_dict):

    # for cityflow engine
    thread_num = 1
    
    # Dir name where roadnet is stored and results will be saved
    road_network = road_network
    
    # config file dir\n",
    dir_config_file = f'Simulation_Results/{road_network}/config.json'

    # number of simulation rounds
    number_of_rounds = 1

    # Predefined phases
    all_phases = phase_definitions()
    
    # store the specific phase for each intersection
    intersection_phase = {}
    
    # define the number of movements
    movements = 12

    # tl-update interval
    delta = 20

    # idle time (idle time <= delta)
    idle_time = 5

    # simulation duration
    sim_duration = 4000

    # saturation flow rate
    saturation_flow = 0.7

    # capacity of a lane (can load a json file in initialization.py with individual capacities)
    capacity = 15
    

    common_params = {
        "thread_num": thread_num,
        "dir_config_file": dir_config_file,
        "road_network": road_network,
        "number_of_rounds": number_of_rounds,
        "all_phases": all_phases,
        "intersection_phase": intersection_phase,
        "movements": movements,
        "delta": delta,
        "idle_time": idle_time,
        "sim_duration": sim_duration,
        "saturation_flow": saturation_flow, # could be made specific for each lane
        "capacity": capacity
    }
    
    return common_params


def load_parameters_Fixed_Time():
    # Additional parameters specific for Fixed Time Control
    
    normal_phase_sequence = [0, 2, 1, 3]
    top_intersection = [0, 1, 2]
    bottom_intersection = [0, 1, 2]
    left_intersection = [0, 1, 2]
    intersection_16_9_phase_sequence = [0, 3, 2, 4, 1]
    intersection_17_9_phase_sequence = [0, 3, 2, 1]
    intersection_16_6_phase_sequence = [0, 3, 2, 1]
    intersection_17_6_phase_sequence = [0, 3, 2, 4, 1]
    
    
    fixed_time_params = {
        "normal_intersection": normal_phase_sequence,
        "top_intersection": top_intersection,
        "bottom_intersection": bottom_intersection,
        "left_intersection": left_intersection,
        "intersection_16_9": intersection_16_9_phase_sequence,
        "intersection_17_9": intersection_17_9_phase_sequence,
        "intersection_16_6": intersection_16_6_phase_sequence,
        "intersection_17_6": intersection_17_6_phase_sequence
    }
    
    return fixed_time_params

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
    scaling = 2
    
    # number of planning steps (actual horizon is * scaling)
    prediction_horizon = 2
    
    # number of tl updates within the prediction horizon time span
    num_tl_updates = ((prediction_horizon * scaling) // common_params["delta"]) + 1
    
    # number of vehicles that enter from the outside per time step
    exogenous_inflow = common_params["saturation_flow"] * scaling
    
    # saturation flow rate
    saturation_flow = common_params["saturation_flow"] * scaling
    
    # discount parameter
    alpha = 0.5                                                                               
    
    
    centralized_params = {
        "prediction_horizon": prediction_horizon,
        "num_tl_updates": num_tl_updates,
        "scaling": scaling,
        "exogenous_inflow": exogenous_inflow,
        "saturation_flow": saturation_flow,
        "alpha": alpha
    }
    
    return centralized_params
    

def load_parameters_LDPP(algorithm, common_params):
    # Additional parameters specific to Centralized algorithm
    
    # maximal number of iterations for the ADMM algorithm
    max_it = 30
    
    # lagrangian parameter rho
    rho = 3
    
    # determine domain for z ("binary" or "continuous") --> affects z-update
    z_domain = "binary"
    
    # saturation flow (not the flow, but the maximal number of cars that flow during 1 delta cycle)
    saturation_flow = common_params["saturation_flow"] * common_params["delta"]
    
    LDPP_params = {
        "max_it": max_it,
        "rho": rho,
        "z_domain": z_domain,
        "saturation_flow": saturation_flow,
    }
    
    if "LDPP-T" in algorithm:
        L = 10
        V1 = 1
        V2 = 1
        V3 = 5
        temp = {"L": L, "V1": V1, "V2": V2, "V3": V3}
        
    elif "LDPP-GF" in algorithm:
        lane_weight = "constant" # or traffic_dependent
        gamma = 1 # if lane_weight == "constant", choose the weight (or could be chosen to be different per lane in initialization.py)
        V = 10
        temp = {"lane_weight": lane_weight, "gamma": gamma, "V": V}
        
    else:
        print(f"WRONG ALGORITHM NAME: {algorithm}! Choose either LDPP-T or LDPP-GF.")
    
    
    LDPP_params.update(temp)
    
    return LDPP_params
    
    

def load_parameters(algorithm, road_network, ext_dict = None):
    common_params = load_parameters_common(road_network, ext_dict)
    
    if algorithm == "Fixed-Time":
        fixed_time_params = load_parameters_Fixed_Time()
        common_params.update(fixed_time_params)
    elif algorithm == "MP":
        mp_params = load_parameters_MP()
        common_params.update(mp_params)
    elif algorithm == "CA_MP":
        ca_mp_params = load_parameters_CA_MP()
        common_params.update(ca_mp_params)
    elif algorithm == "Centralized":
        centralized_params = load_parameters_Centralized(common_params)
        common_params.update(centralized_params)
    elif "LDPP" in algorithm:
        centralized_params = load_parameters_LDPP(algorithm, common_params)
        common_params.update(centralized_params)
    else:
        raise ValueError("Unsupported algorithm: {}".format(algorithm))
        
    # in case parameters are loaded from outside of this function, we will overwrite the values here
    # otherwise use the values defined above
    # this allows for running multiple rounds of simulation with different parameters
    common_params.update(ext_dict)
    
    return common_params



