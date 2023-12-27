import random

def determine_phases(sim, DET, optimal_phases, objective, count_optima, consensus):
    
    # Shuffle the order of update in each round to represent reality (where everything is decentralized) better
    shuffled_intersection_id = list(sim.intersections_data.keys())
    random.shuffle(shuffled_intersection_id)

    for intersection in sim.intersections_data.keys():

        # if the intersection has already terminated, we skip it
        if DET[intersection]:
            continue

        # if the intersection has found consensus with its neighbours, then its own phase and the phase of its
        # neigbours will be fixed
        if consensus:
            for neighbour in sim.intersections_data[intersection]["neighbours"].union({intersection}):
                DET[neighbour] = True

        else:
            # start with assumption that intersection has the smallest objective
            smallest_objective = True

            for neighbour in sim.intersections_data[intersection]["neighbours"]:
                if DET[neighbour] == False:
                    if objective[intersection] > objective[neighbour]:
                        smallest_objective = False

                    # in case the objective values are exactly the same, then the intersection with the smallest index will be chosen
                    elif objective[intersection] == objective[neighbour]:
                        if shuffled_intersection_id.index(intersection) > shuffled_intersection_id.index(neighbour):
                            smallest_objective = False


            if smallest_objective:
                DET[intersection] = True
                # choose phase based on votes from neighbours
                optimal_phases[intersection] = count_optima[intersection]