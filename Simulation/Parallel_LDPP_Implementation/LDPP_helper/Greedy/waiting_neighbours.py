import ray

def waiting_neighbours_values(global_state, arguments, it, intersection, terminated):

    # retrieve neighbouring optimization variables from shared dictionary
    neighbours_optimal_phase = {}
    neighbours_objective = {}
    
    for neighbour in arguments["intersections_data"][intersection]["neighbours"]:
        
        # if the neighbour has already terminated, then it won't update its values anymore
        if terminated[neighbour]:
            continue
            
        # get value from global state
        while True:
            # retrieve the value from it
            previous_opt_phase, previous_obj = ray.get(global_state.get_optimal_values.remote(it, neighbour))
            if previous_opt_phase is not None and previous_obj is not None:
                break
                
        neighbours_optimal_phase[(it, neighbour)] = previous_opt_phase
        neighbours_objective[(it, neighbour)] = previous_obj
        

        
    return neighbours_optimal_phase, neighbours_objective


def waiting_neighbours_DET_consensus(global_state, arguments, it, intersection, terminated):
    
    neighbours_DET_consensus = {}
    
    for neighbour in arguments["intersections_data"][intersection]["neighbours"]:
        
        # if the neighbour has already terminated, then it won't update its values anymore
        if terminated[neighbour]:
            continue
            
        # get value from global state
        while True:
            # retrieve the value from it
            # for DET, we get the value from the previous round (if the agent has finished)
            # for DET_determined, we get the value from this round, as we just now checked for consensus in this round
            DET_consensus = ray.get(global_state.get_DET_consensus.remote(it, neighbour))
            if DET_consensus is not None:
                break
                
        neighbours_DET_consensus[(it,neighbour)] = DET_consensus
        
    return neighbours_DET_consensus


def waiting_neighbours_DET(global_state, arguments, it, intersection, terminated):
    
    neighbours_DET = {}
    
    for neighbour in arguments["intersections_data"][intersection]["neighbours"]:
        
        # if the neighbour has already terminated, then it won't update its values anymore
        if terminated[neighbour]:
            continue
            
        # get value from global state
        while True:
            # retrieve the value from it
            # for DET, we get the value from the previous round (if the agent has finished)
            # for DET_determined, we get the value from this round, as we just now checked for consensus in this round
            DET = ray.get(global_state.get_DET.remote(it, neighbour))
            if DET is not None:
                break
                
        neighbours_DET[(it, neighbour)] = DET
            
        
    return neighbours_DET


def waiting_neighbours_terminated(global_state, arguments, intersection):
    
    neighbours_terminated = {}
    
    for neighbour in arguments["intersections_data"][intersection]["neighbours"]:
        
        # do not need while loop, as value is always set
        terminated = ray.get(global_state.get_terminated.remote(neighbour))
                
        neighbours_terminated[neighbour] = terminated
            
        
    return neighbours_terminated