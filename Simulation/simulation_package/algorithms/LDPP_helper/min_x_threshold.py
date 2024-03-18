import gurobipy as gp
from gurobipy import GRB
import numpy as np
import ray
from collections import defaultdict

from .ADMM.ADMM_opt_objective import ADMM_objective
from .Greedy.fix_phases_constraint import fix_phases

@ray.remote(num_cpus = 1)
def min_x(pressure_per_phase, arguments, agent_intersection, z = None, lambda_ = None, DET = None, determined_phases = None):
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
    
    determined_phases : dict
        Used in the Greedy algorithm that stores the optimal phase for each intersection in each round
        In this function it is only used in case a neighbour has already terminated (this phase won't change anymore)
        For neighbour's that are still running, "determined_phases" won't be used
        
        
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
    
    # add this line due to a bug in Gurobi v11, that calculates the norm wrongly. Will be fixed in v11.0.1
    m.setParam("DualReductions", 0)
    
    # a list with all neighbouring intersections including agent_intersection
    neighbouring_intersections = arguments["intersections_data"][agent_intersection]["neighbours"].union({agent_intersection})
    
    # set the big M constant (* 2 + 30 as a "safety" margin)
    big_M = max(arguments["params"]["capacity"].values()) * 2 + 30
    
    # all inflowing lanes into this intersection
    all_inflow_lanes = arguments["intersections_data"][agent_intersection]["inflow"]
    max_movement_id = max(arguments["lanes_data"][lane][1] for lane in all_inflow_lanes)
    
    
    # only used for defining variables (only 1 h1 and h2 variable for 2 lanes that share the same id)
    movement_sorted_lanes = {}
    movement_sorted_d_lanes = defaultdict(list)

    for movement_id in range(max_movement_id + 1):
        movement_sorted_lanes[movement_id] = [lane for lane in all_inflow_lanes if arguments["lanes_data"][lane][1] == movement_id]
        first_lane = movement_sorted_lanes[movement_id][0]
        unique_set = set()
        downstream_lanes = arguments["lanes_data"][first_lane][3]
        
        for d_lane in downstream_lanes:
            movement_d_lane = arguments["lanes_data"][d_lane][1]
            # !!!!!! ASSUME THAT THERE ARE ONLY LANES WITH MAX 4 LANES (2 STRAIGHT LANES) 
            condition = ((len(downstream_lanes) == 4) and (not d_lane.endswith("2"))) or (len(downstream_lanes) <= 3)
            if ((movement_d_lane is not None) and movement_d_lane not in unique_set) or ((movement_d_lane is None) and condition):
                unique_set.add(movement_d_lane)
                movement_sorted_d_lanes[first_lane].append(d_lane)
                
                
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
    
    # only take the first lane (0th element) to keep naming consistent
    h1 = m.addVars([lanes[0] for lanes in movement_sorted_lanes.values()], vtype=GRB.BINARY, name="h1")

    h2 = m.addVars(
        [
            (in_lanes[0], d_lane)
            for in_lanes in movement_sorted_lanes.values()
            for d_lane in movement_sorted_d_lanes[in_lanes[0]]
        ],
        vtype=GRB.BINARY,
        name="h2"
    )
    
    # Greedy algorithm needs an extra set of constraints to fix the phases that are already determined
    if "Greedy" in arguments["algorithm"]:
        fix_phases(m, x, DET, determined_phases, agent_intersection, neighbouring_intersections)
    
    # Add constraints such that there is only one phase active in one intersection
    for neighbour in neighbouring_intersections:
        m.addConstr(x.sum(neighbour, "*") == 1, name=f"phase_{neighbour}")
    
    
    # define a linear part for the pressure function and penalty
    pressure = gp.LinExpr(0)
    pen = gp.LinExpr(0)
    
    # define a quadratic expression for the ADMM consensus part
    ADMM_obj = gp.QuadExpr(0)
    
    # add the standard pressure to the objective (MAX problem)
    for neighbour in neighbouring_intersections:
        
        neighbours_phase_type = arguments["params"]["intersection_phase"][neighbour]
        
        # count past decisions
        unique, counts = np.unique(arguments["phase_history"][neighbour], return_counts=True)
        count_decisions = dict(zip(unique, counts))
            
        for phase in arguments["params"]["all_phases"][neighbours_phase_type]:
            pressure.add(x[neighbour, phase], pressure_per_phase[neighbour][phase])
            
            # 3rd penalty term (V3 * (# of lanes in phase) * (# of previous decisions))
            pen.add(x[neighbour, phase], arguments["params"]["V3"] * len(arguments["params"]["all_phases"][neighbours_phase_type]) * count_decisions.get(phase, 0))
            
            
    # add penalty function to the objective                        
    for movement_id in range(max_movement_id + 1):
        
        ##################### OUTFLOW LANE #####################
        
        # determine which lanes have this movement_id (potentially more than 1)
        current_lanes = movement_sorted_lanes[movement_id]
        
        # determine phase type for this intersection
        intersection_phase_type = arguments["params"]["intersection_phase"][agent_intersection]
        
        # find out which phases includes that movement_id
        corresponding_phase_lane = [phase for phase, movement_list in arguments["params"]["all_phases"][intersection_phase_type].items() if movement_id in movement_list]
        
        # determine amount of cars that can leave the lane
        outflow_lane = sum(min(arguments["lane_vehicle_count"][lane], arguments["params"]["saturation_flow"]) for lane in current_lanes)
        
        # add the outflow to the objective
        outflow_gurobi = gp.LinExpr(0)
        
        for phase in corresponding_phase_lane:
            outflow_gurobi.add(x[agent_intersection, phase], outflow_lane)
            
        
        ##################### INFLOW LANE #####################
            
        # get a list with all upstream lanes
        upstream_lane = arguments["lanes_data"][current_lanes[0]][2]
        
        # define a gurobi expression for the inflow
        inflow_gurobi = gp.LinExpr(0)
        
        # check if there are upstream lanes
        if upstream_lane:
            for u_lane in upstream_lane:
                
                # movement_id of upstream lane
                movement_u_lane = arguments["lanes_data"][u_lane][1]
                intersection_u_lane = arguments["lanes_data"][u_lane][0]
                
                # find out which phases includes that movement_id
                u_intersection_phase_type = arguments["params"]["intersection_phase"][intersection_u_lane]
                corresponding_u_phase_lane = [phase for phase, movement_list in arguments["params"]["all_phases"][u_intersection_phase_type].items() if movement_u_lane in movement_list]
                
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
        downstream_lanes = arguments["lanes_data"][current_lanes[0]][3]
        
        # define empty dict
        outflow_d_gurobi = {d_lane: gp.LinExpr(0) for d_lane in downstream_lanes}
        
        # if the d_lane has no downstream lanes, then d_lane is an exit lane and has a constant outflow
        for d_lane in downstream_lanes:
            
            # check if the downstream lanes is an exit lane (if yes, constant outflow)
            if len(arguments["lanes_data"][d_lane][3]) != 0:

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
                d_intersection_phase_type = arguments["params"]["intersection_phase"][intersection_d_lane]
                corresponding_d_phase_lane = [phase for phase, movement_list in arguments["params"]["all_phases"][d_intersection_phase_type].items() if movement_d_lane in movement_list]

                # add the outflow from d_lane to the objective
                for phase in corresponding_d_phase_lane:
                    outflow_d_gurobi[d_lane].add(x[intersection_d_lane, phase], outflow_d_lane)
            
            else:
                outflow_d_gurobi[d_lane].add(arguments["params"]["saturation_flow"]) 
        
        ##################### H1 PENALTY #####################
        neighboring_lanes = [l for l in arguments["lanes_data"] if l[:-2] in current_lanes[0]]
        
        # assume uniform turn ratios (in case current_lane is larger than 1)
        R = 1/(len(neighboring_lanes) - len(current_lanes) + 1)
        
        num_vehicles_lanes = sum(arguments["lane_vehicle_count"][lane] for lane in current_lanes)
        num_lanes = len(current_lanes)
        
        # Big M constraint 1
        m.addConstr(num_vehicles_lanes - outflow_gurobi + inflow_gurobi*R >= num_lanes * arguments["params"]["capacity"][current_lanes[0]] - big_M * (1 - h1[current_lanes[0]]), name=f"h1_1_{current_lanes[0]}")
        
        # Big M constraint 2
        m.addConstr(num_vehicles_lanes - outflow_gurobi + inflow_gurobi*R <= num_lanes * arguments["params"]["capacity"][current_lanes[0]] + big_M * h1[current_lanes[0]], name=f"h1_2_{current_lanes[0]}")
        
        # weight the value by the lane's weight
        pen.add(h1[current_lanes[0]], arguments["params"]["V1"] * arguments["params"]["constant_weight"][current_lanes[0]])
        
        
        ##################### H2 PENALTY #####################
        # determine if two d_lanes share the same movement_id
        # !!!!!!! ASSUMES THERE EXISTS ONLY ROADS WITH 4 OR LESS LANES AND THE ONLY "DOUBLE" LANE IS GOING STRAIGHT !!!!!!!
        downstream_groups = defaultdict(list)
        for index, lane in enumerate(downstream_lanes):
            movement_d_lane = arguments["lanes_data"][d_lane][1]
            if movement_d_lane == None:
                if (len(downstream_lanes) <= 3) or (len(downstream_lanes) == 4 and (not lane.endswith('2'))):
                    downstream_groups[index].append(lane)
            else:
                downstream_groups[arguments["lanes_data"][lane][1]].append(lane)
    
        for d_group in downstream_groups.values():
            
            # in case there are multiple lanes with the same movement id, we sum the total number of vehicles and total number of outflowing cars in d_lane
            num_vehicles_d_lanes = 0
            total_outflow_d_gurobi = gp.LinExpr(0)
            for d_lane in d_group:
                num_vehicles_d_lanes += arguments["lane_vehicle_count"][d_lane]
                total_outflow_d_gurobi += outflow_d_gurobi[d_lane]
                
            num_d_lanes = len(d_group)
        
            # Big M constraint 1
            m.addConstr(num_vehicles_d_lanes - total_outflow_d_gurobi + outflow_gurobi >= num_d_lanes * arguments["params"]["capacity"][d_group[0]] - big_M * (1 - h2[current_lanes[0], d_group[0]]), name=f"h2_1_{current_lanes[0]}_{d_group[0]}")

            # Big M constraint 2
            m.addConstr(num_vehicles_d_lanes - total_outflow_d_gurobi + outflow_gurobi  <= num_d_lanes * arguments["params"]["capacity"][d_group[0]] + big_M * h2[current_lanes[0], d_group[0]], name=f"h2_2_{current_lanes[0]}_{d_group[0]}")

            # weight the value by the lane's weight
            pen.add(h2[current_lanes[0], d_group[0]], arguments["params"]["V2"] * arguments["params"]["constant_weight"][d_group[0]])
        

    
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
    if status == GRB.INF_OR_UNBD:
        print("The model is infeasible or unbounded")
        m.computeIIS()
        m.write("model.ilp")

    # write the optimal results in a dictionary
    x_optimized = {}
    for neighbour in neighbouring_intersections:
        # do round as otherwise sometimes this could lead to some issues with dtype=int
        x_optimized[neighbour] = np.array([round(x_phase.X) for x_phase in x.select(neighbour, '*')], dtype=int)
        assert sum(x_optimized[neighbour]) == 1, f"sum is {sum(x_optimized[neighbour])}" # safety condition

    obj_val = m.ObjVal
    pressure_val = pressure_per_phase[agent_intersection][np.argmax(x_optimized[agent_intersection])]
    
    m.dispose()

    return agent_intersection, x_optimized, obj_val, pressure_val
        
                
                
            
    
    
    
    