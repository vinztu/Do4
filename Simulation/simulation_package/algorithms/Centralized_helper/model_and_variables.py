import gurobipy as gp
from gurobipy import GRB

def create_model_and_variables(sim):
    """ Create the gurobi model and all necessary optimization variables"""
    
    max_capacity = max(sim.params["capacity"].values())
    
    # define a set with all road names
    road_names = set([lane[:-2] for lane in sim.lanes_data])
    
    # define gurobi model
    model = gp.Model(env = sim.gurobi_env)
    #model.setParam("NonConvex", 2)
    model.setParam("DualReductions", 0)
    
    
    # variables for phi
    phi = model.addVars(
        [
            (num_tl_update, intersection, phase)
            for num_tl_update in range(sim.params["num_tl_updates"])
            for intersection in sim.intersections_data.keys()
            for phase in sim.params["all_phases"][sim.params["intersection_phase"][intersection]]
        ],
        vtype = GRB.BINARY,
        name = "phi"
    )
    
    
    # variables for q (the variable for time t=0 is not needed (constant))
    q = model.addVars(range(1,sim.params["prediction_horizon"] + 1), sim.lanes_data.keys(), vtype = GRB.CONTINUOUS, lb = 0, ub = max_capacity, name = "q")
    
    # pressure per movement
    p_m = model.addVars(sim.params["prediction_horizon"] + 1, sim.intersections_data.keys(), sim.params["movements"], lb = -2*max_capacity, ub = 2*max_capacity, vtype = GRB.CONTINUOUS, name = "p_m")
    
    # pressure per phase
    p_p = model.addVars(
        [
            (prediction_horizon, intersection, phase)
            for prediction_horizon in range(sim.params["prediction_horizon"] + 1)
            for intersection in sim.intersections_data.keys()
            for phase in sim.params["all_phases"][sim.params["intersection_phase"][intersection]]
        ],
        lb = -7 * max_capacity,
        ub = 7 * max_capacity,
        vtype = GRB.CONTINUOUS,
        name = "p_p"
    )
    
    # inflow variables (min between q and saturation flow)
    min_flow = model.addVars(sim.params["prediction_horizon"] + 1, sim.lanes_data.keys(), lb = 0, ub = sim.params["saturation_flow"], vtype = GRB.CONTINUOUS, name = "min_flow")
        
    # outflow variable (max number of cars on a lane)
    max_lane = model.addVars(sim.params["prediction_horizon"] + 1, road_names, lb = 0, ub = max_capacity, vtype = GRB.CONTINUOUS, name = "max_lane")
        
    # outflow variable (free capacity left ona downstream lane)
    free_capacity = model.addVars(sim.params["prediction_horizon"] + 1, road_names, lb = 0, ub = max_capacity, vtype = GRB.CONTINUOUS, name = "free_capacity")
    
    # outflow variable (actual outflow respecting downstream lanes)
    outflow = model.addVars(sim.params["prediction_horizon"] + 1, sim.lanes_data.keys(), lb = 0, ub = sim.params["saturation_flow"], vtype = GRB.CONTINUOUS, name = "outflow")
    
    
    # combine them into a dict
    opt_vars = {
        "phi": phi,
        "q": q,
        "p_m": p_m,
        "p_p": p_p,
        "min_flow": min_flow,
        "max_lane": max_lane,
        "free_capacity": free_capacity,
        "outflow": outflow
    }
    
    return model, opt_vars
    