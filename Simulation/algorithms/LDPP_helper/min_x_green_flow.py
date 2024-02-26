import gurobipy as gp
from gurobipy import GRB
import numpy as np
import ray

from Simulation.algorithms.LDPP_helper.ADMM.ADMM_opt_objective import ADMM_objective
from Simulation.algorithms.LDPP_helper.Greedy.fix_phases_constraint import fix_phases
   
            
@ray.remote
def min_x(pressure_per_phase, arguments, agent_intersection, z = None, lambda_ = None, DET = None, optimal_phases = None):
    """ Gurobi model and solver for minimizing the x variable for the ADMM-update 
    The continuous penalty is implemented here
    
    Arguments:
    ------------
    
    pressure_per_phase : dict{list}
        A dictionary with intersection id as keys and the inner list consists of the pressure per phase
        
    arguments : dict
        Contains information about the sim object (Simulation class) such as intersections_data, lanes_data, params
        
    agent_intersection : string
        Intersection id of the agent's intersection 
    
    z : dict
        A dictionary with intersection id's as keys and the binary phase variables as values
    
    lambda_ : dict
        A dictionary with intersection id's as keys and values are another dictionary. That dictionary has 
        neighbouring intersections as keys and binary phase variables as values
        lambda_ are the dual variables
        
    DET : dict
        Used in the Greedy algorithm to determine which intersection has already terminated and which is stil running
        Keys are intersection id's and values are boolean values (True or False)
    
    optimal_phases : dict
        Used in the Greedy algorithm that stores the optimal phase for each intersection in each round
        In this function it is only used in case a neighbour has already terminated (this phase won't change anymore)
        For neighbour's that are still running, "optimal_phases" won't be used
        
        
    Returns:
    ------------
    x_optimized : dict
        Solution of the optimization problem. Keys are the intersection id's and the values is the list with the corresponding phase (1 = active, 0 = not active)
    """
    
    # start gurobi env to supress the output
    env = gp.Env(empty=True)
    env.setParam("OutputFlag",0)
    env.start()
    
    # create a new model
    m = gp.Model(f"min_x_{agent_intersection}", env=env)
    
    # add this line due to a bug in Gurobi v11, that calculates the norm wrongly. Will be fixed in version v11.0.1
    m.setParam("DualReductions", 0)
    
    # a list with all neghbouring intersections
    neighbouring_intersections = arguments["intersections_data"][agent_intersection]["neighbours"].union({agent_intersection})
    
    # determine phase type for this intersection
    intersection_phase_type = arguments["params"]["intersection_phase"][agent_intersection]
    
    # Create variables
    x = m.addVars(
        [
            (intersection, phase)
            for intersection in neighbouring_intersections
            for phase in arguments["params"]["all_phases"][arguments["params"]["intersection_phase"][intersection]]
        ],
        vtype = GRB.BINARY,
        name = "x_i"
    )
    
    # Add constraints such that there is only one phase active in one intersection
    for neighbour in neighbouring_intersections:
        m.addConstr(x.sum(neighbour, "*") == 1, name=f"phase_{neighbour}")
    
    # Greedy algorithm needs an extra set of constraints to fix the phases that are already determined
    #if "Greedy" in arguments["algorithm"]:
    #    fix_phases(m, x, DET, optimal_phases, agent_intersection, neighbouring_intersections)
    
    # define a linear part for the penalty function
    pressure = gp.LinExpr(0)
    pen = gp.LinExpr(0)
    
    # add the standard pressure to the objective (MAX problem)
    for neighbour in neighbouring_intersections:
        neighbours_phase_type = arguments["params"]["intersection_phase"][neighbour]
        
        for phase in arguments["params"]["all_phases"][neighbours_phase_type]:
            pressure.add(x[neighbour, phase], pressure_per_phase[neighbour][phase])
            
    
    # add penalty function to the objective
    for lane in arguments["intersections_data"][agent_intersection]["inflow"]:
        
        # movement_id and downstream lanes of lane
        movement_lane = arguments["lanes_data"][lane][1]
        downstream_lanes = arguments["lanes_data"][lane][3]
    
        # find out which phases includes that movement_id
        corresponding_phase_lane = [phase for phase, movement_list in arguments["params"]["all_phases"][intersection_phase_type].items() if movement_lane in movement_list]
        
        # do not consider right turns (since all phases "activate" them
        if len(corresponding_phase_lane) == len(arguments["params"]["all_phases"][intersection_phase_type]):
            continue
            
        for d_lane in downstream_lanes:
            
            # intersections id and movement id of downstream lane
            intersection_d_lane = arguments["lanes_data"][d_lane][0]
            movement_d_lane = arguments["lanes_data"][d_lane][1]
            
            # check if that d_lane is a an outflowing (out of network) lane
            if intersection_d_lane is None:
                continue
            
            # find out which phaes includes that movement_d_lane
            d_intersection_phase_type = arguments["params"]["intersection_phase"][intersection_d_lane]
            corresponding_phase_d_lane = [phase for phase, movement_list in arguments["params"]["all_phases"][d_intersection_phase_type].items() if movement_d_lane in movement_list]
           
            # check if the lane is a right turn
            # In both cases, we do not consider them
            if len(corresponding_phase_d_lane) == len(arguments["params"]["all_phases"][d_intersection_phase_type]):
                continue
            
            # define penalty weight
            if arguments["params"]["lane_weight"] == "constant":
                gamma = 1
                
            elif arguments["params"]["lane_weight"] == "traffic_dependent":
                gamma = arguments["lane_vehicle_count"][d_lane]
                
            else:
                raise ValueError(f'Wrong arguments["params"]["lane_weight"]: {arguments["params"]["lane_weight"]}')
        
            
            # combine the weights
            weight = arguments["params"]["V"] * gamma
            
            # iterate over all phases that are included
            for phase_lane in corresponding_phase_lane:
                for phase_d_lane in corresponding_phase_d_lane:
                    # subtract (as it is a reward)
                    pen -= weight * x[agent_intersection, phase_lane] * x[intersection_d_lane, phase_d_lane]
    
    
    ##################### ADMM TERMS #####################
    # define a quadratic expression for the ADMM consensus part
    ADMM_obj = gp.QuadExpr(0)
    
    if "ADMM" in arguments["algorithm"]:
        # add ADMM consensus terms
        ADMM_objective(m, arguments, agent_intersection, neighbouring_intersections, x, lambda_, z, ADMM_obj)
        
    
    ##################### COMBINE EVERYTHING AND SOLVE #####################

    # set the objective of the model
    m.setObjective(pressure - pen - ADMM_obj, GRB.MAXIMIZE)

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
        # do round as otherwise sometimes this could lead to some issues with dtype=int
        x_optimized[neighbour] = np.array([round(x_phase.X) for x_phase in x.select(neighbour, '*')], dtype=int)
        assert sum(x_optimized[neighbour]) == 1, f"sum is {sum(x_optimized[neighbour])} for {neighbour}" # safety condition

    
    obj_val = m.ObjVal
    
    pressure_val = pressure_per_phase[agent_intersection][np.argmax(x_optimized[agent_intersection])]
    
    m.dispose()

    return agent_intersection, x_optimized, obj_val, pressure_val