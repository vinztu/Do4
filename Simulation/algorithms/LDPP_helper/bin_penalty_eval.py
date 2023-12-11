import numpy as np

def pen_eval(x, arguments, intersection):
    """
    Binary penalty evaluation (only penalty without pressure)
    
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
    
    # Initilalize penalty parts
    h1 = 0
    h2 = 0
    h3 = 0
    
    # determine current optimal phase for intersection
    current_optimal_phase = np.argmax(x[intersection])
    
    for lane in arguments["intersections_data"][intersection]["inflow"]:
        
        ##################### OUTFLOW LANE #####################
        
        # movement_id of lane
        movement_lane = arguments["lanes_data"][lane][1]
        
        # find out which phases includes that movement_id
        corresponding_phase_lane = [phase for phase, movement_list in arguments["params"]["phases"].items() if movement_lane in movement_list]
        
        
        # if the phase for this lane gets activated, cars can leave that lane
        if current_optimal_phase in corresponding_phase_lane:
            outflow_lane = min(arguments["lane_vehicle_count"][lane], arguments["params"]["saturation_flow"])
        else:
            outflow_lane = 0
            
            
        ##################### INFLOW LANE #####################
        
        # get a list with all upstream lanes
        upstream_lane = arguments["lanes_data"][lane][2]
        
        # initialize a zero inflow
        inflow_lane = 0
        
        # check if there are upstream lanes
        if upstream_lane:
            for u_lane in upstream_lane:
                
                # movement_id of upstream lane
                movement_u_lane = arguments["lanes_data"][lane][1]
                intersection_u_lane = arguments["lanes_data"][lane][0]
                
                # find out which phases includes that movement_id
                corresponding_u_phase_lane = [phase for phase, movement_list in arguments["params"]["phases"].items() if movement_u_lane in movement_list]
                
                # determine current optimal phase for upstream intersection
                current_optimal_phase_u_intersection = np.argmax(x[intersection_u_lane])
                
                # if the upstream phase is activated, then the inflow will increase
                if current_optimal_phase_u_intersection in corresponding_u_phase_lane:
                    inflow_lane += min(arguments["lane_vehicle_count"][u_lane], arguments["params"]["saturation_flow"])
        
        # if no upstream lane exists, we assume a constant inflow (d)
        else:
            inflow_lane += arguments["params"]["saturation_flow"]
            
        
        ##################### OUTFLOW DOWNSTREAM LANE #####################
        
        # all downstream lanes for lane
        downstream_lanes = arguments["lanes_data"][lane][3]
        
        # initialize empty downstream dict
        outflow_d_lane = {}
    
        for d_lane in downstream_lanes:

            # initilize this value with 0 outflow
            outflow_d_lane[d_lane] = 0

            # movement_id of the downstream lane
            movement_d_lane = arguments["lanes_data"][d_lane][1]
            intersection_d_lane = arguments["lanes_data"][d_lane][0]

            # if the downstream lane is an exit lane (no intersection_d_lane), then the outflow is constant
            # and does not depend on a traffic light
            if not intersection_d_lane:
                outflow_d_lane[d_lane] = min(arguments["lane_vehicle_count"][d_lane], arguments["params"]["saturation_flow"])
                continue

            # find out which phases includes that of movement_id
            corresponding_d_phase_lane = [phase for phase, movement_list in arguments["params"]["phases"].items() if movement_d_lane in movement_list]

            # determine current optimal phase for downstream intersection
            current_optimal_phase_d_intersection = np.argmax(x[intersection_d_lane])

            # if the downstream phase is activated, then the outflow increases
            if current_optimal_phase_d_intersection in corresponding_d_phase_lane:
                outflow_d_lane[d_lane] = min(arguments["lane_vehicle_count"][d_lane], arguments["params"]["saturation_flow"])
                    
                
        
        ##################### H1 PENALTY #####################
        neighboring_lanes = [l for l in all_lane_id_dict if l[:-2] in lane]
        
        # assume uniform turn ratios
        R = 1/len(neighboring_lanes)
        
        if arguments["lane_vehicle_count"][lane] - outflow_lane + inflow_lane*R >= arguments["params"]["capacity"][lane[:-2]]:
            h1 += 1 * arguments["params"]["constant_weight"][lane]
            
        ##################### H2 PENALTY #####################
        if downstream_lanes:
            for d_lane in downstream_lanes:
                if arguments["lane_vehicle_count"][d_lane] - outflow_d_lane[d_lane] + outflow_lane >= arguments["params"]["capacity"][d_lane[:-2]]:
                    h2 += 1 * arguments["params"]["constant_weight"][lane]
                    
        
        ##################### H3 PENALTY #####################
        # we do not have to sum up over all phases as only the term with the current_optimal_phase gives a non-zero value
        h3 += np.count_nonzero(arguments["phase_history"] == current_optimal_phase) * arguments["params"]["constant_weight"][lane]
    
    
    
    # combine all penalty terms
    penalty = h1 * arguments["params"]["V1"] + h2 * arguments["params"]["V2"] + h3 * arguments["params"]["V3"]
        
        
    return penalty