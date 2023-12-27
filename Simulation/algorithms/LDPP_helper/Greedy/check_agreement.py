import numpy as np
import ray


def check_agreement(sim, arguments_id, optimal_phases, DET, consensus, count_optima):
    futures = []
        
    # Then, check wether the decisions of some intersection coincide
    # If yes, then set DET = True accordingly
    # Parallel maximization of min_x function
    for intersection in sim.intersections_data:
        if DET[intersection] == False:
            # This remote call returns a future, a so-called Ray object reference
            futures.append(agent_check_agreement.remote(arguments_id, intersection, optimal_phases, DET))

    # Fetch futures with ray.get and write it in a dict
    consensus_results = ray.get(futures)

    for intersection, cons, c_o in consensus_results:
        consensus[intersection] = cons
        count_optima[intersection] = c_o
        

@ray.remote
def agent_check_agreement(arguments, agent_intersection, optimal_phases, DET):
    
    # initialize a counter that counts which phase will be chosen most based on neighbours
    count_optima = np.zeros(len(arguments["params"]["phases"]))
    
    # initialize consensus as true
    consensus = True
                            
    # a list with all neghbouring intersections
    neighbouring_intersections = arguments["intersections_data"][agent_intersection]["neighbours"]
    
    # in case all neighbours have already terminated, choose count_optima = optimal phase and terminate in the next round
    active_neighbours = sum(DET[neighbour] for neighbour in neighbouring_intersections)
    if active_neighbours == 0:
        consensus = True
        # count_optima does not matter anymore
        return agent_intersection, consensus, count_optima
    
    
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
                if not np.all(neighbours_optimum == optimal_phases[agent_intersection][check_intersection]):
                
                    # no consensus for all intersection and their phases
                    consensus = False
                
                # if check_intersection == agent_intersection, we care what other intersections prefer to choose for agent_intersection in case that agent_intersection has the smallest objective value among neighbours
                if check_intersection == agent_intersection:
                
                    # increase the vote for that phase by 1
                    count_optima[neighbours_optimum] += 1
                    
                    
                    
    return agent_intersection, consensus, count_optima