import ray

def waiting_x_and_lambda_neighbours(arguments, it, intersection, global_state):
    """ Waiting until neighbours have computed their x_i values (and lambda_, in case of binary z domain)
    and then return their values as a dict
    
    Returns
    ---------
    neighbours_xi : dict
        Keys: neighbours intersection id's, values: list with binary xi (len(phases))
    
    neighbours_lambda_: dict
        Keys: neighbours intersection id's, values: list with binary lambda_ (len(phases))
        
    """
    # retrieve neighbouring optimization variables from shared dictionary
    neighbours_x = {}
    neighbours_lambda_ = {}
    
    for neighbour in arguments["intersections_data"][intersection]["neighbours"]:
        # get x from global state
        while True:
            # retrieve the value from it
            previous_x_it_decision = ray.get(global_state.get_x.remote(it, neighbour))
            if previous_x_it_decision is not None:
                break
                
        neighbours_x[(it, neighbour)] = previous_x_it_decision

        
        # in case z is binary, retrieve lambda_ values from neighbours
        if arguments["params"]["z_domain"] == "binary":
            while True:
                # only can take the value from iteration it - 1 (not it )
                previous_lambda_it_decision = ray.get(global_state.get_lambda_.remote(it - 1, neighbour))
                if previous_lambda_it_decision is not None:
                    break
            
            neighbours_lambda_[(it - 1, neighbour)] = previous_lambda_it_decision
        
    return neighbours_x, neighbours_lambda_


def waiting_z_g_neighbours(arguments, it, intersection, global_state):
    # retrieve neighbouring optimization variables from shared dictionary
    neighbours_z_g = {}
    
    for neighbour in arguments["intersections_data"][intersection]["neighbours"]:
        # get x from global state
        while True:
            previous_z_g_it_decision = ray.get(global_state.get_z_g.remote(it, neighbour))
            if previous_z_g_it_decision is not None:
                break
                
        neighbours_z_g[(it, neighbour)] = previous_z_g_it_decision
        
    return neighbours_z_g