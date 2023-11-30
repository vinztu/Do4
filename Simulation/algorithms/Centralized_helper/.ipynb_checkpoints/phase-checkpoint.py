import gurobipy as gp
from gurobipy import GRB

def set_phase_constraints(sim, model, opt_vars):
    """ set the constraints such that only 1 phase can be active at a time"""
    
    for tl_update in range(sim.params["num_tl_updates"]):
        for intersection in sim.intersections_data:
            
            model.addConstr((
                1 == gp.quicksum(opt_vars["phi"][tl_update, intersection, phase] for phase in sim.params["phases"])
                ),
                name = f"phi_{tl_update}_{intersection}"
            )