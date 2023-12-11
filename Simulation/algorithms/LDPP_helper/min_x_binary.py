def min_x(z, lambda_, pressure_per_phase, arguments, env, intersection):
    """ Gurobi model and solver for minimizing the x variable for the ADMM-update 
    The binary penalty is implemented here
    
    Arguments:
    ------------
    
    z : dict
        A dictionary with intersection id's as keys and the binary phase variables as values
    
    lambda_ : dict
        A dictionary with intersection id's as keys and values are another dictionary. That dictionary has 
        neighbouring intersections as keys and binary phase variables as values
        lambda_ are the dual variables
        
    pressure_per_phase : dict{list}
        A dictionary with intersection id as keys and the inner list consists of the pressure per phase
        
    arguments : dict
        Contains information about the sim object (Simulation class) such as intersections_data, lanes_data, params
    
    env
        A gurobi environment. Used to suppress the output during the gurobi optimization steps
    
    intersection : string
        Intersection id of the agent's intersection 
        
        
    Returns:
    ------------
    x_optimized : dict
        Solution of the optimization problem. Keys are the intersection id's and the values is the list with the corresponding phase (1 = active, 0 = not active)
    """
    
    # create a new model
    m = gp.Model(f"min_x_{intersection}", env=env)
    
    # a list with all neighbouring intersections
    neighbouring_intersections = arguments["intersections_data"][intersection]["neighbours"].union({intersection})
    
    # set the big M constant (+10 as a "safety" margin)
    big_M = max(arguments["params"]["capacity"].values()) + 10
    
    # Create variables
    x = m.addVars(neighbouring_intersections, len(arguments["params"]["phases"]), vtype=GRB.BINARY, name="x_i")

    
    # Add constraints such that there is only one phase active in one intersection
    for intersection in neighbouring_intersections:
        m.addConsr(x.sum(intersection, "*") == 1, name=f"phase_{intersection}")
    
    
    # define a quadratic expression, since we have the norm squared
    obj = gp.QuadExpr()
    
    # add the standard pressure to the objective (MAX problem)
    for intersection in neighbouring_intersections:
        
        # count past decisions
        unique, counts = np.unique(past_decisions[intersection], return_counts=True)
        count_decisions = dict(zip(unique, counts))
            
        for phase in arguments["params"]["phases"]:
            obj.add(x[intersection, phase], pressure_per_phase[intersection][phase])
            
            # 3rd penalty term (V3 * (# of lanes in phase) * (# of previous decisions))
            obj.add(x[intersection, phase], - arguments["params"]["V3"] * len(arguments["params"]["phases"]) * count_decisions.get(phase, 0) * arguments["params"]["constant_weight"][lane])
            
            
    # add penalty function to the objective
    for lane in arguments["intersections_data"][intersection]["inflow"]:
        
        ##################### OUTFLOW LANE #####################
        
        # movement_id of lane
        movement_lane = arguments["lanes_data"][lane][1]
        
        # find out which phases includes that movement_id
        corresponding_phase_lane = [phase for phase, movement_list in arguments["params"]["phases"].items() if movement_lane in movement_list]
        
        # determine amount of cars that can leave the lane
        outflow_lane = min(arguments["lane_vehicle_count"][lane], arguments["params"]["saturation_flow"])
        
        # add the outflow to the objective
        outflow_gurobi = gp.LinExpr(0)
        
        for phase in corresponding_phase_lane:
            outflow_gurobi.add(x[intersection, phase], outflow_lane)
            
        
        ##################### INFLOW LANE #####################
            
        # get a list with all upstream lanes
        upstream_lane = arguments["lanes_data"][lane][2]
        
        # define a gurobi expression for the inflow
        inflow_gurobi = gp.LinExpr(0)
        
        # check if there are upstream lanes
        if upstream_lane:
            for u_lane in upstream_lane:
                
                # movement_id of upstream lane
                movement_u_lane = arguments["lanes_data"][lane][1]
                intersection_u_lane = arguments["lanes_data"][lane][0]
                
                # find out which phases includes that movement_id
                corresponding_u_phase_lane = [phase for phase, movement_list in arguments["params"]["phases"].items() if movement_u_lane in movement_list]
                
                # determine amount of cars that can leave the u_lane
                inflow_lane = min(arguments["lane_vehicle_count"][u_lane], arguments["params"]["saturation_flow"])
                
                # add the inflow to the objective
                for phase in corresponding_u_phase_lane:
                    inflow_gurobi.add(x[intersection_u_lane, phase], inflow_lane)
                    
        
        # if no upstream lane exists, we assume a constant inflow (d)
        else:
            inflow_gurobi.add(arguments["params"]["saturation_flow"])
            
        
        ##################### OUTFLOW DOWNSTREAM LANE #####################
    
        # all downstream lanes for lane
        downstream_lanes = arguments["lanes_data"][lane][3]
        
        # define empty dict
        outflow_d_gurobi = {d_lane: gp.LinExpr(0) for d_lane in downstream_lanes}
        
        for d_lane in downstream_lanes:

            # movement_id of the downstream lane
            movement_d_lane = arguments["lanes_data"][d_lane][1]
            intersection_d_lane = arguments["lanes_data"][d_lane][0]
            
            # determine amount of cars that can leave d_lane
            outflow_d_lane = min(arguments["lane_vehicle_count"][d_lane], arguments["params"]["saturation_flow"])

            # if the downstream lane is an exit lane (no intersection_d_lane), then the outflow is constant
            # and does not depend on a traffic light
            if not intersection_d_lane:
                outflow_d_gurobi[d_lane] = outflow_d_lane
                continue

            # find out which phases includes that of movement_id
            corresponding_d_phase_lane = [phase for phase, movement_list in arguments["params"]["phases"].items() if movement_d_lane in movement_list]

            # add the outflow from d_lane to the objective
            for phase in corresponding_d_phase_lane:
                outflow_d_gurobi[d_lane].add(x[intersection_d_lane, phase], outflow_d_lane)
            
        
        ##################### H1 PENALTY #####################
        neighboring_lanes = [l for l in all_lane_id_dict if l[:-2] in lane]
        
        # assume uniform turn ratios
        R = 1/len(neighboring_lanes)
        
        # Big M constraint 1
        m.addConsr(arguments["lane_vehicle_count"][lane] - outflow_gurobi + inflow_gurobi*R >= arguments["params"]["capacity"][lane[:-2]] - big_M * (1 - h1[lane]), name=f"h1_1_{lane}")
        
        # Big M constraint 2
        m.addConsr(arguments["lane_vehicle_count"][lane] - outflow_gurobi + inflow_gurobi*R <= arguments["params"]["capacity"][lane[:-2]] + big_M * h1[lane], name=f"h1_2_{lane}")
        
        # weight the value by the lane's weight
        obj.add(h1[lane], arguments["params"]["V1"] * arguments["params"]["constant_weight"][lane])
        
        
        ##################### H2 PENALTY #####################
        if downstream_lanes:
            for d_lane in downstream_lanes:
                # Big M constraint 1
                m.addConsr(arguments["lane_vehicle_count"][d_lane] - outflow_d_gurobi[d_lane] + outflow_gurobi >= arguments["params"]["capacity"][d_lane[:-2]] - big_M * (1 - h2[lane, d_lane]), name=f"h2_1_{lane}_{d_lane}")
                
                # Big M constraint 2
                m.addConsr(arguments["lane_vehicle_count"][d_lane] - outflow_d_gurobi[d_lane] + outflow_gurobi  >= arguments["params"]["capacity"][d_lane[:-2]] + big_M * h2[lane, d_lane], name=f"h2_2_{lane}_{d_lane}")
                
                # weight the value by the lane's weight
                obj.add(h2[lane, d_lane], arguments["params"]["V2"] * arguments["params"]["constant_weight"][d_lane])
        

    

    # ADMM consensus terms
    for intersection in neighbouring_intersections:
        # ADD ADMM PART


    # set the objective of the model
    m.setObjective(obj, GRB.MAXIMIZE)

    # optimize model
    m.optimize()

    # check for status of the optimization problem
    status = m.Status
    if status == GRB.UNBOUNDED:
        print("The model is unbounded")
    if status == GRB.INFEASIBLE:
            print('The model is infeasible')
            m.computeIIS()
            m.write("model.ilp")


    # write the optimal results in a dictionary
    x_optimized = {}
    for neighbour in neighbouring_intersections:
        x_optimized[neighbour] = np.array([x_phase.X for x_phase in x.select(neighbour, '*')], dtype=int)
        assert sum(x_optimized[neighbour]) == 1 # asdkfjalskdjflakdsjfaöklsdjföajsdfasdlfjlaskdjfaskd

    m.dispose()

    return x_optimized
        
                
                
            
    
    
    
    