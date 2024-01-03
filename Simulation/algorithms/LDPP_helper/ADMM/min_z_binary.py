import gurobipy as gp
from gurobipy import GRB
import numpy as np
import ray

@ray.remote
def min_z(arguments, agent_intersection, x, lambda_):
    """
    Solve min z problem to get only the optimal for element z_g
    """
    
    # start gurobi env to supress the output
    env = gp.Env(empty=True)
    env.setParam("OutputFlag",0)
    env.start()
    
    # create a new model
    m = gp.Model(f"min_z_{agent_intersection}", env=env)
    
    # a list with all neghbouring intersections
    neighbouring_intersections = arguments["intersections_data"][agent_intersection]["neighbours"].union({agent_intersection})
    
    # Create variables
    z = m.addVars(len(arguments["params"]["phases"]), vtype=GRB.BINARY, name="z")
    
    # add constraint such that there is only 1 active phase per intersection
    m.addConstr(z.sum() == 1, name=f"z_constr")
    
    
    # define a linear expression for the ADMM consensus part
    ADMM_obj = gp.LinExpr(0)
    
    # instead of interating over all M(i,j) = g, we iterate over all neighbours,
    # since each neighbour holds 1 entry, such that M(i,j) = g
    for neighbour in neighbouring_intersections:
        
        # add the first term to the objective (lambda * z)
        ADMM_obj += lambda_[neighbour][agent_intersection] @ z.select("*")

        # add the second term to the objective (rho * x * z)
        ADMM_obj += arguments["params"]["rho"] * x[neighbour][agent_intersection] @ z.select("*")
        
    
    # set the objective value
    m.setObjective(ADMM_obj, GRB.MAXIMIZE)
    
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


    # save the optimal results
    z_optimized = np.array([z_phase.X for z_phase in z.select()], dtype=int)

    m.dispose()

    return agent_intersection, z_optimized