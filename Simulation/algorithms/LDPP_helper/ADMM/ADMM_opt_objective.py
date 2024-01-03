import gurobipy as gp
from gurobipy import GRB

def ADMM_objective(m, arguments, agent_intersection, neighbouring_intersections, x, lambda_, z, ADMM_obj):
    """
    ##################### ADMM TERMS #####################
    """
    
    diff = m.addVars(neighbouring_intersections, len(arguments["params"]["phases"]), vtype=GRB.CONTINUOUS, lb = -2, ub = 2, name="diff")
    norm = m.addVars(neighbouring_intersections, vtype=GRB.CONTINUOUS, name="norm_ADMM")
    
    for neighbour in neighbouring_intersections:
        
        # First Term (add 1 lambda * x term to the objective) (includes len(phases) terms)
        ADMM_obj.add(lambda_[agent_intersection][neighbour].T @ x.select(neighbour, '*'))
        
        
        # Difference between x and z
        m.addConstrs((
                    diff[neighbour, phase] == x[neighbour, phase] - z[neighbour][phase]
                    for phase in arguments["params"]["phases"]
                    ),
                    name = f"diff_{neighbour}"
        )
        
        # LAST TERM
        m.addGenConstrNorm(norm[neighbour], diff.select(neighbour, '*'), 2.0, "normconstr")
        ADMM_obj += norm[neighbour]*norm[neighbour]*arguments["params"]["rho"]/2