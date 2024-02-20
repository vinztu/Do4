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
    
    # determine phase type for this intersection
    intersection_phase_type = arguments["params"]["intersection_phase"][agent_intersection]
    
    # Create variables
    z = m.addVars(len(arguments["params"]["all_phases"][intersection_phase_type]), vtype=GRB.BINARY, name="z")
    
    diff = m.addVars(
        [
            (neighbour, phase)
            for phase in arguments["params"]["all_phases"][arguments["params"]["intersection_phase"][agent_intersection]]
            for neighbour in neighbouring_intersections
        ],
        vtype=GRB.CONTINUOUS,
        lb = -2,
        name="diff",
    )
    
    norm = m.addVars(neighbouring_intersections, vtype=GRB.CONTINUOUS, name="norm")
    
    # add constraint such that there is only 1 active phase per intersection
    m.addConstr(z.sum() == 1, name=f"z_constr")
    
    # define a linear expression for the ADMM consensus part
    ADMM_obj = gp.QuadExpr(0)
    
    # instead of interating over all M(i,j) = g, we iterate over all neighbours,
    # since each neighbour holds 1 entry, such that M(i,j) = g
    for neighbour in neighbouring_intersections:
                
        m.addConstrs((
            diff[neighbour, phase] == x[neighbour][agent_intersection][phase] - z[phase]
            for phase in arguments["params"]["all_phases"][intersection_phase_type]
            ),
            name = f"diff_{neighbour}"
        )
        
        # SECOND TERM
        ADMM_obj.add(lambda_[neighbour][agent_intersection].T @ diff.select(neighbour, '*'))
            
        # LAST TERM
        m.addGenConstrNorm(norm[neighbour], diff.select(neighbour, '*'), 2.0, "normconstr")
        
        # add the squared norm to the objective
        ADMM_obj.add(norm[neighbour] * norm[neighbour] * arguments["params"]["rho"]/2)
        
    
    # set the objective value
    m.setObjective(ADMM_obj, GRB.MINIMIZE)
    
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
    z_optimized = np.array(np.round([z_phase.X for z_phase in z.select()]), dtype=int)

    m.dispose()

    return agent_intersection, z_optimized