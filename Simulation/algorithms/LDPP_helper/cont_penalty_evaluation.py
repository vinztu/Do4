def pen_eval(x, arguments, intersection):
    """
    Continuous penalty evaluation (only penalty without pressure)
    
    Arguments:
    ------------
    
    x : dict
        A dictionary with intersection id's as keys and the binary phase variables as values
        
    arguments : dict
        Contains information about the sim object (Simulation class) such as intersections_data, lanes_data, params
    
    intersection : string
        Intersection id of the agent's intersection 
        
        
    Returns:
    ------------
    penalty : float
        Total penalty value for this penalty function
    """
    
    total_penalty = 0.0
    
    for lane in arguments["intersections_data"][intersection]["inflow"]:
        
        # movement_id and downstream lanes of lane
        movement_lane = arguments["lanes_data"][lane][1]
        downstream_lanes = arguments["lanes_data"][lane][3]
        
        # find out which phases includes that movement_id
        corresponding_phase_lane = [phase for phase, movement_list in arguments["params"]["phases"].items() if movement_lane in movement_list]
        
        # do not consider right turns (since all phases "activate" them
        if len(corresponding_phase_lane) == len(arguments["params"]["phases"]):
            continue
            
        for d_lane in downstream_lanes:
            
            # intersections id and movement id of downstream lane
            intersection_d_lane = arguments["lane_data"][0]
            movement_d_lane = arguments["lane_data"][1]
            
            # find out which phaes includes that movement_d_lane
            corresponding_phase_d_lane = [phase for phase, movement_list in arguments["params"]["phases"].items() if movement_d_lane in movement_list]
            
            # check if that d_lane is a an outflowing (out of network) lane or if it is a right turn
            # In both cases, we do not consider them
            if len(corresponding_phase_d_lane) == 0 or len(corresponding_phase_d_lane) == len(arguments["params"]["phases"]):
                continue
            
            # define penalty weight
            if arguments["params"]["lane_weight"] == "Constant":
                gamma = arguments["params"]["constant_weight"][lane]
                
            elif arguments["params"]["lane_weight"] == "traffic_dependent":
                gamma = arguments["lane_vehicle_count"][d_lane]
                
            else:
                print(f'Wrong arguments["params"]["lane_weight"]: {Wrong arguments["params"]["lane_weight"]}')
                
            
            penalty = arguments["params"]["V"] * gamma
            
            
            # iterate over all phases that are included
            for phase_lane in corresponding_phase_lane:
                for phase_d_lane in corresponding_phase_d_lane:
                    if x[intersection_lane][phase_lane] == 1 and x[intersection_d_lane][phase_d_lane] == 1:
                        # subtracted (as it is a reward)
                        total_penalty -= penalty
        
        
    return total_penalty