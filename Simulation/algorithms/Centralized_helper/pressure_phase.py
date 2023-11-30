import gurobipy as gp
from gurobipy import GRB

def compute_pressure_per_phase(sim, model, opt_vars):
    """ Compute the pressure per phase and add it to the model"""
    
    for tau in range(sim.params["prediction_horizon"] + 1):
        for intersection in sim.intersections_data:
            for phase, movement_list in sim.params["phases"].items():
                
                model.addConstr((
                    opt_vars["p_p"][tau, intersection, phase] == gp.quicksum(opt_vars["p_m"][tau, intersection, movement] for movement in movement_list)
                    ),
                    name = f"p_p_{tau}_{intersection}_{phase}"
                )