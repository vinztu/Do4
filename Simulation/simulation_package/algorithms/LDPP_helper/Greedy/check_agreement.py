import numpy as np


def check_agreement(sim, agent_intersection, optimal_phases, DET):
    
    # determine phase type for this intersection
    intersection_phase_type = sim.params["intersection_phase"][agent_intersection]
    
    # initialize a counter that counts which phase will be chosen most based on neighbours
    count_optima = np.zeros(len(sim.params["all_phases"][intersection_phase_type]))
    
    # initialize consensus as true
    consensus = True
                            
    # a list with all neghbouring intersections
    neighbouring_intersections = sim.intersections_data[agent_intersection]["neighbours"]
    
    # in case all neighbours have already terminated, choose count_optima = optimal phase and terminate in the next round
    active_neighbours = sum(DET[neighbour] for neighbour in neighbouring_intersections)
    if active_neighbours == len(neighbouring_intersections):
        consensus = True
        # count_optima does not matter anymore
        return consensus, count_optima
    
    
    # check for agreement with all neighbours
    for neighbour in neighbouring_intersections:
        
        # if the neighbour has already finished his computation, we don't consider him anymore
        if DET[neighbour]:
            continue
        
        # check wether neighbours decision match with agent_intersections decision
        # we do the for loop here in case neighbour and agent_intersection have more common neighbours
        # e.g. "triangle" roadmap
        for check_intersection in neighbouring_intersections.union({agent_intersection}):
            
            # in case the agent_intersection's neighbour is not a neighbour to the check_intersection, it will return a None
            neighbours_optimum = optimal_phases[neighbour].get(check_intersection, None)
            
            # if the neighbour exists
            if neighbours_optimum is not None:
                
                # in case any of the decisions do not match, consensus is not found yet
                if np.any(neighbours_optimum != optimal_phases[agent_intersection][check_intersection]):
                
                    # no consensus for all intersection and their phases
                    consensus = False
                
                # if check_intersection == agent_intersection, we care what other intersections prefer to choose for agent_intersection in case that agent_intersection has the smallest objective value among neighbours
                if check_intersection == agent_intersection:
                    # increase the vote for that phase by 1
                    count_optima[np.argmax(neighbours_optimum)] += 1
                    
                    
                    
    return consensus, count_optima