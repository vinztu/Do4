import gurobipy as gp
from gurobipy import GRB

from pprint import pprint

def optimizer(sim, model, opt_vars):
    """ Calls the optimizer from gurobi and retrieves the optimal solution"""
    
    try:
        # call the gurobi optimizer
        model.optimize()
        
        model.write("new.lp")
        
        # status of the optimization
        status = model.Status
        
        if status == GRB.UNBOUNDED:
            raise ValueError("The model is unbounded")
        if status == GRB.INFEASIBLE:
            model.computeIIS()
            model.write("model.ilp")
            raise ValueError("The model is infeasible")
            
        optimal_phases = {}
        for intersection in sim.intersections_data:
            
            # determine phase type for this intersection
            intersection_phase_type = sim.params["intersection_phase"][intersection]
            
            # do a rounding operation due to some numerical errors in the solution
            opt_phase = [round(opt_vars["phi"][0, intersection, phase].X) for phase in sim.params["all_phases"][intersection_phase_type]].index(1)
            optimal_phases[intersection] = opt_phase
            
            # take only the pressure at time t = 0 into consideration
            sim.perform["current_pressure"][intersection] = opt_vars["p_p"][0, intersection, opt_phase].X
            
            # take the sum of pressures over the prediction horizon into consideration
            sim.perform["current_objective"][intersection] = calculate_objective_per_intersection(sim, opt_vars, intersection)
            
            
    except gp.GurobiError as e:
        print("Error code " + str(e.errno) + ": " + str(e))
    
    except AttributeError:
        print(f"Encountered an attribute error: {AttributeError}")
    
    return optimal_phases



def calculate_objective_per_intersection(sim, opt_vars, intersection):
    """ Calculates the objective per intersection instead of the whole network"""
    
    obj_per_int = 0
    
    for tau in range(sim.params["prediction_horizon"] + 1):
        
        tl_update = (tau * sim.params["scaling"]) // sim.params["delta"]
        
        # determine phase type for this intersection
        intersection_phase_type = sim.params["intersection_phase"][intersection]
        
        # find out the optimal phase for intersection at time tau
        opt_phase = [round(opt_vars["phi"][tl_update, intersection, phase].X) for phase in sim.params["all_phases"][intersection_phase_type]].index(1)
        
        # determine the corresponding pressure for that phase
        obj_per_int += (sim.params["alpha"] ** tau) * opt_vars["p_p"][tau, intersection, opt_phase].X
        
    return obj_per_int
        