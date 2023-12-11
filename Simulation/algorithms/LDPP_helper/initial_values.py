import copy

def create_initial_values(arguments):
    """ Creates initial variables for the ADMM algorithm. It initializes all of them by
    a matrix that only contains one 1 per row

    Parameters
    ----------
    sim : Simulation
        Object of the Simulation Class

    Returns
    -------
    x : dict
        A dictionary with intersection id's as keys and values are another dictionary. That dictionary has 
        neighbouring intersections as keys and binary phase variables as values
    
    phi : dict
        A dictionary with intersection id's as keys and binary phase variables as values
    
    lambda_ : dict
        A dictionary with intersection id's as keys and the corresponding value is another dictionary. That dictionary has 
        neighbouring intersections as keys and binary phase variables as values
        lambda_ are the dual variables
    """
    
    
    # ------------------------------------------------------------------------------------------------------------------
    
    x = {intersection: None for intersection in arguments["intersections_data"]}
    phi = {intersection: None for intersection in arguments["intersections_data"]}
    lambda_ = {intersection: None for intersection in arguments["intersections_data"]}
    
    
    for intersection in sim.intersections_data:
        
        temp_dict = {}
        
        for neighbour in arguments["intersections_data"][intersection]["neighbours"]:
            x_i = np.zeros(arguments["params"]["phases"] , dtype=bool)
            
            # set 1 random entry to 1
            idx = np.random.randint(arguments["params"]["phases"])
            x_i[idx] = 1
            
            temp_dict[neighbour] = x_i
            
            
        # set initial values for all x, lambda and phi optimization variables
        x[current_intersection] = temp_dict.copy()
        lambda_[current_intersection] = temp_dict.copy()
        phi[current_intersection] = x_i.copy()
        
        
    return x, phi, lambda_