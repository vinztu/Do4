import numpy as np
import ray

def check_agreement(arguments, agent_intersection, optimal_phase, it, terminated, DET, global_state):
    
    # initialize a counter that counts which phase will be chosen most based on neighbours
    count_optima = np.zeros(len(arguments["params"]["phases"]))
    
    # initialize consensus as true
    consensus = True
                            
    # a list with all neghbouring intersections
    neighbouring_intersections = arguments["intersections_data"][agent_intersection]["neighbours"]
    
    
    # check for agreement with all neighbours
    for neighbour in neighbouring_intersections:
        
        # if the neighbour has already finished his computation, we don't consider him anymore
        if DET[(it - 1, neighbour)]:
            #print(f"check terminated agent {agent_intersection} neighbour {neighbour}")
            continue
        
        # check wether neighbours decision match with agent_intersections decision
        # we do the for loop here in case neighbour and agent_intersection have more common neighbours
        # e.g. "triangle" roadmap
        for check_intersection in neighbouring_intersections.union({agent_intersection}):
            
            # in case the agent_intersection's neighbour is not a neighbour to the neighbour, it will return a None
            neighbours_optimum = optimal_phase[(it, neighbour)].get(check_intersection, None)
            
            # if tha neighbour exists
            if neighbours_optimum is not None:
                
                # in case any of the decisions do not match, consensus is not found yet
                if not np.all(neighbours_optimum == optimal_phase[(it, agent_intersection)][check_intersection]):
                
                    # no consensus for all intersection and their phases
                    consensus = False
                
                # if check_intersection == agent_intersection, we care what other intersections "think" about it
                if check_intersection == agent_intersection:
                
                    # increase the vote for that phase by 1
                    count_optima[neighbours_optimum] += 1
                    
                    
    return consensus, count_optima