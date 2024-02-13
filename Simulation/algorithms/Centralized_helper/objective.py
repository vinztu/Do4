import gurobipy as gp
from gurobipy import GRB

def set_objective(sim, model, opt_vars):
    
    obj = gp.LinExpr(0)
    
    for tau in range(sim.params["prediction_horizon"] + 1):
        
        tl_update = (tau * sim.params["scaling"]) // sim.params["delta"]
        
        for intersection in sim.intersections_data:
            
            # determine phase type for this intersection
            intersection_phase_type = sim.params["intersection_phase"][intersection]
            
            for phase in sim.params["all_phases"][intersection_phase_type]:
                obj += (sim.params["alpha"]**tau) * opt_vars["p_p"][tau, intersection, phase] * opt_vars["phi"][tl_update, intersection, phase]
                
                
    model.setObjective(obj, GRB.MAXIMIZE)