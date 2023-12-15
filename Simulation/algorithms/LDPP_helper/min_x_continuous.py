import gurobipy as gp
from gurobipy import GRB
import numpy as np

def min_x(z_g, lambda_, pressure_per_phase, arguments, env, agent_intersection, it):
    """ Gurobi model and solver for minimizing the x variable for the ADMM-update 
    The continuous penalty is implemented here
    
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
    m = gp.Model(f"min_x_{agent_intersection}", env=env)
    
    # a list with all neghbouring intersections
    neighbouring_intersections = arguments["intersections_data"][agent_intersection]["neighbours"].union({agent_intersection})
    
    # Create variables
    x = m.addVars(neighbouring_intersections, len(arguments["params"]["phases"]), vtype=GRB.BINARY, name="x_i")
    diff = m.addVars(neighbouring_intersections, len(arguments["params"]["phases"]), vtype=GRB.CONTINUOUS, lb = -2, ub = 2, name="diff")
    norm = m.addVars(neighbouring_intersections, vtype=GRB.CONTINUOUS, name="norm_ADMM")
    
    
    # Add constraints such that there is only one phase active in one intersection
    for neighbour in neighbouring_intersections:
        m.addConsr(x.sum(neighbour, "*") == 1, name=f"phase_{neighbour}")
    
    
    # define a linear part for the penalty function
    f_i = gp.LinExpr(0)
    
    # define a quadratic expression for the ADMM consensus part
    ADMM_obj = gp.QuadExpr(0)
    
    # add the standard pressure to the objective (MAX problem)
    for neighbour in neighbouring_intersections:
        for phase in arguments["params"]["phases"]:
            f_i.add(x[neighbour, phase], pressure_per_phase[neighbour][phase])
            
    
    # add penalty function to the objective
    for lane in arguments["intersections_data"][agent_intersection]["inflow"]:
        
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
            intersection_d_lane = arguments["lane_data"][d_lane][0]
            movement_d_lane = arguments["lane_data"][d_lane][1]
            
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
                print(f'Wrong arguments["params"]["lane_weight"]: {arguments["params"]["lane_weight"]}')
        
        
            penalty = arguments["params"]["V"] * gamma
            
            # iterate over all phases that are included
            for phase_lane in corresponding_phase_lane:
                for phase_d_lane in corresponding_phase_d_lane:
                    # add (as it is a reward)
                    f_i += penalty * x[intersection_lane][phase_lane] * x[intersection_d_lane][phase_d_lane]
                    
        
    ##################### ADMM TERMS #####################
    # negative since its a maximization problem
    for neighbour in neighbouring_intersections:
        
        # First Term (add 1 lambda * x term to the objective) (includes len(phases) terms)
        ADMM_obj.add( -lambda_[(it, agent_intersection)][neighbour].T @ x.select(neighbour, '*'))
        
        
        # Difference between x and z
        m.addConstrs((
                    diff[neighbour, phase] == x[neighbour, phase] - z_g[neighbour][phase]
                    for phase in arguments["params"]["phases"]
                    ),
                    name = f"diff_{neighbour}"
        )
        
        # LAST TERM
        m.addGenConstrNorm(norm[neighbour], diff.select(neighbour, '*'), 2.0, "normconstr")
        ADMM_obj -= norm[neighbour]*norm[neighbour]*RHO/2


        
    
    ##################### COMBINE EVERYTHING #####################

    # set the objective of the model
    m.setObjective(f_i + ADMM_obj, GRB.MAXIMIZE)

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

    m.dispose()
    
    x_agent = {(it + 1, agent_intersection): x_optimized}

    return x_optimized