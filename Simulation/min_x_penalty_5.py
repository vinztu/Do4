import gurobipy as gp
from gurobipy import GRB
import numpy as np



def min_x(current_intersection, phi, lambda_, pressure_per_phase, lane_vehicle_count, roadnet_info, PARAMETERS, PHASES):
    """ Computes the first step of the ADMM algorithm. It finds the minimium x value with penalty function 1 and an additional term --> penalty 5

    Parameters
    ----------
    env
        A gurobi environment. Used to suppress the output for gurobi optimizations
        
    current_intersection : string
        The id of the current intersection.

    phi : dict
        A dictionary with intersection id's as keys and the binary phase variables as values.
    
    lambda_ : dict
        A dictionary with intersection id's as keys and values are another dictionary. That dictionary has 
        neighbouring intersections as keys and binary phase variables as values
        lambda_ are the dual variables
        
    pressure_per_phase: dict{list}
        A dictionary with intersection id as keys and the inner list consists of the pressure per phase
 
    lane_vehicle_count : dict
        A dictionary with all lanes as keys and corresponding number of vehicles as values
        
    roadnet_info : dict
        A dictionary with all information about the roadnet file (see initialization.py)
    
    PARAMETERS : dict
        A dictionary with all parameters used in the simulation
    
    PHASES : dict
        A dictionary where the keys are the number of the phase and the values is the list with the corresponding allowed movement
         
    Returns
    -------
    phi : dict
        A dictionary with intersection id's as keys and the optimal binary phase variables as values.
    """
    
    # Algorithm parameters
    Q_MAX = PARAMETERS["Q_MAX"]
    MAX_FLOW = PARAMETERS["MAX_FLOW"]
    V1 = PARAMETERS["V1"]
    V2 = PARAMETERS["V2"]
    V3 = PARAMETERS["V3"]
    RHO = PARAMETERS["RHO"]
    
    past_decisions = roadnet_info["past_decisions"]
    
    # Further modifications
    WITH_OUTFLOW = PARAMETERS["WITH_OUTFLOW"]
    
    # roadnet info
    neighbouring_intersections = roadnet_info["neighbouring_intersections_dict"][current_intersection]
    intersection_to_lane = roadnet_info["intersection_to_lane_dict"][current_intersection] # all inflowing lanes into the current intersection
    all_lane_id_dict = roadnet_info["all_lane_id_dict"]
    
    # ------------------------------------------------------------------------------------------------------------------
    
    # set gurobi environment output to 0
    env = gp.Env(empty=True)
    env.setParam("OutputFlag",0)
    env.start()
    
    # Create a new model
    m = gp.Model(f"min_x_{current_intersection}", env=env)
    
    # set the big M constant (+10 is a "safety" margin)
    big_M = Q_MAX + 30
    
    # Create variables    
    x = m.addVars(neighbouring_intersections, len(PHASES), vtype=GRB.BINARY, name="x_i")
    h_1 = m.addVars(intersection_to_lane, vtype=GRB.BINARY, name="h_1")
    diff = m.addVars(neighbouring_intersections, len(PHASES), vtype=GRB.CONTINUOUS, lb = -2, ub = 2, name="diff")
    norm = m.addVars(neighbouring_intersections, vtype=GRB.CONTINUOUS, name="norm_ADMM")
    
    h_2 = m.addVars(
        [
            (in_lane, d_lane)
            for in_lane in intersection_to_lane
            for d_lane in all_lane_id_dict[in_lane][3]
        ],
        vtype=GRB.BINARY,
        name="h_2"
    )

    
    # Add row constraints such that there is only one active phase in one intersection
    for neighbour in neighbouring_intersections:
        
        # At most one active phase per intersection / row
        m.addConstr(x.sum(neighbour, '*') == 1, name=f"neighbour_{neighbour}")
        
    # define a quadratic expression (instead of linear), since we have the norm squared 
    obj = gp.QuadExpr()
    

    # add standard pressure to the objective and the 3rd penalty term
    for intersection in neighbouring_intersections:
        
        # count past decisions
        unique, counts = np.unique(past_decisions[intersection], return_counts=True)
        count_decisions = dict(zip(unique, counts))
        
        for phase in PHASES:
            # standard pressure (NEGATIVE since we want to maximize the pressure)
            obj.add(x[intersection, phase], -pressure_per_phase[intersection][phase])
            
            # 3rd penalty term (V3 * (# of lanes in phase) * (# of previous decisions))
            obj.add(x[intersection, phase], V3 * len(PHASES[phase]) * count_decisions.get(phase, 0))
            
    
    # add penalty function to the objective
    for lane in intersection_to_lane:
    
        #################################
        ########## OUTFLOW LANE ##########
        #################################

        movement_lane = all_lane_id_dict[lane][1]

        # find out which phases includes that movement id
        corresponding_phase_lane = [phase for phase, movement_list in PHASES.items() if movement_lane in movement_list]
        
        # define maximal amount of cars that can leave lane
        amount_of_cars_on_lane = lane_vehicle_count[lane]
        
        outflow_lane = min(amount_of_cars_on_lane, MAX_FLOW)
        
        # define a gurobi expression for the outflow
        outflow_gurobi = gp.LinExpr()
        for phase in corresponding_phase_lane:
            outflow_gurobi.add(x[current_intersection, phase], outflow_lane)


        #################################
        ########## INFLOW LANE ##########
        #################################
        
        # get a list with all upstream lanes
        upstream_lanes = all_lane_id_dict[lane][2]
        
        # define a gurobi expression for the inflow
        inflow_gurobi = gp.LinExpr(0)

        # check if there are upstream lanes
        if upstream_lanes:
            
            for u_lane in upstream_lanes:

                # movement id of upstream lane
                movement_u_lane = all_lane_id_dict[u_lane][1]
                intersection_u_lane = all_lane_id_dict[u_lane][0]

                # find out which phases includes that movement id
                corresponding_u_phase_lane = [phase for phase, movement_list in PHASES.items() if movement_u_lane in movement_list]

                amount_of_cars_on_u_lane = lane_vehicle_count[u_lane]
                inflow_lane = min(amount_of_cars_on_u_lane, MAX_FLOW)
                
                # define a gurobi expression for the inflow
                for phase in corresponding_u_phase_lane:
                    inflow_gurobi.add(x[intersection_u_lane, phase], inflow_lane)
                    
        # Else assume constant inflow
        else:
            inflow_gurobi.add(MAX_FLOW)

        ###################################
        ########## OUFLOW D-LANE ##########
        ###################################

        # get a list with all downstream lanes
        downstream_lanes = all_lane_id_dict[lane][3]
        
        # check if there are downstream lanes
        if downstream_lanes:

            outflow_d_gurobi = {d_lane: gp.LinExpr() for d_lane in downstream_lanes}
            
            for d_lane in downstream_lanes:

                # movement id of upstream lane
                movement_d_lane = all_lane_id_dict[d_lane][1]
                intersection_d_lane = all_lane_id_dict[d_lane][0]
                
                # if the downstream lane is an exit lane (no corresponding intersection), then there is no green light for this lane
                # Thus, all cars (up to the MAX_FLOW) can leave the lane
                if not intersection_d_lane:
                    amount_of_cars_on_d_lane = lane_vehicle_count[d_lane]
                    outflow_d_gurobi[d_lane].add(min(amount_of_cars_on_d_lane, MAX_FLOW))
                    continue

                # find out which phases includes that movement id
                corresponding_d_phase_lane = [phase for phase, movement_list in PHASES.items() if movement_d_lane in movement_list]

                amount_of_cars_on_d_lane = lane_vehicle_count[d_lane]
                outflow_d_lane = min(amount_of_cars_on_d_lane, MAX_FLOW)
                
                # define a gurobi expression for the inflow
                for phase in corresponding_d_phase_lane:
                    outflow_d_gurobi[d_lane].add(x[intersection_d_lane, phase], outflow_d_lane)
        
        # else assume constant outflow
        else:
            for d_lane in downstream_lanes:
                outflow_d_gurobi[d_lane].add(MAX_FLOW)


        ################################
        ########## H1 Penalty ##########
        ################################
        
        # define turn ratio (uniform assumption)
        neighboring_lanes = [l for l in all_lane_id_dict if l[:-2] in lane]
        R = 1/len(neighboring_lanes)
        
        # use a big-M notation to convert x>y --> 1 to 2 equations
        if WITH_OUTFLOW:
            m.addConstr(amount_of_cars_on_lane - outflow_gurobi + inflow_gurobi * R >= Q_MAX - big_M * (1 - h_1[lane]), name=f"h_1_condition_1_{lane}")
            m.addConstr(amount_of_cars_on_lane - outflow_gurobi + inflow_gurobi * R <= Q_MAX + big_M * h_1[lane], name=f"h_1_condition_2_{lane}")
        
        else:
            m.addConstr(amount_of_cars_on_lane + inflow_gurobi * R >= Q_MAX - big_M * (1 - h_1[lane]), name=f"h_1_condition_1_{lane}")
            m.addConstr(amount_of_cars_on_lane + inflow_gurobi * R <= Q_MAX + big_M * h_1[lane], name=f"h_1_condition_2_{lane}")
        
        
        ################################
        ########## H2 Penalty ##########
        ################################

        if downstream_lanes:
            for d_lane in downstream_lanes:
                amount_of_cars_on_d_lane = lane_vehicle_count[d_lane]
                
                # use a big-M notation to convert x>y --> 1 to 2 equations
                if WITH_OUTFLOW:
                    m.addConstr(amount_of_cars_on_d_lane - outflow_d_gurobi[d_lane] + outflow_gurobi >= Q_MAX - big_M * (1 - h_2[lane, d_lane]), name=f"h_2_condition_1_{lane}_{d_lane}")
                    m.addConstr(amount_of_cars_on_d_lane - outflow_d_gurobi[d_lane] + outflow_gurobi <= Q_MAX + big_M * h_2[lane, d_lane], name=f"h_2_condition_2_{lane}_{d_lane}")
                
                else:
                    m.addConstr(amount_of_cars_on_d_lane + outflow_gurobi >= Q_MAX - big_M * (1 - h_2[lane, d_lane]), name=f"h_2_condition_1_{lane}_{d_lane}")
                    m.addConstr(amount_of_cars_on_d_lane + outflow_gurobi <= Q_MAX + big_M * h_2[lane, d_lane], name=f"h_2_condition_2_{lane}_{d_lane}")

                
                
    ############################           
    # add penalty
    obj.add(V1 * h_1.sum())
    obj.add(V2 * h_2.sum())
        
        
    # add ADMM terms to the objective
    for neighbour in neighbouring_intersections:
        
        m.addConstrs((
                    diff[neighbour, phase] == x[neighbour, phase] - phi[neighbour][phase]
                    for phase in PHASES
                    ),
                    name = f"diff_{neighbour}"
        )
        
        # SECOND TERM
        obj.add(lambda_[current_intersection][neighbour].T @ diff.select(neighbour, '*'))
        
        # LAST TERM
        m.addGenConstrNorm(norm[neighbour], diff.select(neighbour, '*'), 2.0, f"normconstr_{neighbour}")
        obj.add(norm[neighbour]*norm[neighbour]*RHO/2)
    
        
    # minimize the objective, since we added the pressure negatively
    m.setObjective(obj, GRB.MINIMIZE)
    
    m.update()
    #m.write(f"Min_x_{current_intersection}.lp")

    # Optimize model
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
        x_optimized[neighbour] = np.array(np.round([x_phase.X for x_phase in x.select(neighbour, '*')]), dtype=int)
        assert sum(x_optimized[neighbour]) == 1
    
    # update the past decision dictionary
    
    m.dispose()
    env.dispose()
    
    return x_optimized     