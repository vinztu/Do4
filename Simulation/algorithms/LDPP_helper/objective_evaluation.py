def obj_eval(x, pressure_per_phase, arguments, intersection):
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
    
    # find all neighbouring intersections
    neighbouring_intersections = arguments["intersections_data"][intersection]["neighbours"]
 
    pressure = 0
    
    # Add the standard pressure (according to Varaiya)
    for inter in neighbouring_intersections.union({intersection}):
        
        # using x_i here to evaluate the objective
        optimal_phase_for_neighbour = np.argmax(x[inter])
        pressure += pressure_per_phase[inter][optimal_phase_for_neighbour]
        
    
    # Add the penalty values
    pen = pen_eval(x, arguments, intersection)
   
    # combine the 2 values
    objective = pressure - pen
    
    return objective