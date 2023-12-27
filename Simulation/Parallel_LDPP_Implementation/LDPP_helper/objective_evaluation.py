import numpy as np
from Simulation.algorithms.LDPP_helper.eval_threshold_pen import pen_eval as threshold_pen
from Simulation.algorithms.LDPP_helper.eval_green_flow_pen import pen_eval as green_flow_pen


        
def import_function(arguments):
    if "LDPP-T" in arguments["algorithm"]:
        return threshold_pen
    elif "LDPP-GF" in arguments["algorithm"]:
        return green_flow_pen
    else:
        print(f'WRONG ALGORITHM {arguments["algorithm"]}')

        
        
def obj_eval(x, pressure_per_phase, arguments, agent_intersection, it):
    """ Computes the whole objective value. We use the local variable x here to compute the it.
    
    Formulated as a maximization problem (NOT MIN)

    Parameters
    ----------
    x : dict
        A dictionary with intersection id's as keys and binary phase variables as values
        
    pressure_per_phase: dict{list}
        A dictionary with intersection id as keys and the inner list consists of the pressure per phase
        
    arguments : dict

    intersection : string
        The id of the current intersection.
        
    Returns
    -------
    objective : float
        Returns the computed objective value
    """
    
    # import the correct function
    pen_eval = import_function(arguments)
    
    # find all neighbouring intersections
    neighbouring_intersections = arguments["intersections_data"][agent_intersection]["neighbours"].union({agent_intersection})
 
    pressure = 0
    
    
    # Add the standard pressure (according to Varaiya)
    for neighbour in neighbouring_intersections:
        
        # using x_i here to evaluate the objective
        optimal_phase_for_neighbour = np.argmax(x[(it, neighbour)][neighbour])
        pressure += pressure_per_phase[neighbour][optimal_phase_for_neighbour]
        
        
    
    # Add the penalty values
    pen = pen_eval(x, arguments, agent_intersection, it)
   
    # combine the 2 values
    objective = pressure - pen
    
    return pressure, objective