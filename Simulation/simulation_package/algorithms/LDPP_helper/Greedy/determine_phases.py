import random
import numpy as np
import copy

from .update_objective import update_objective

from ..evaluate_objective_threshold import evaluate_objective as evaluate_objective_threshold
from ..evaluate_objective_green_flow import evaluate_objective as evaluate_objective_green_flow

from .check_agreement import check_agreement

def import_evaluation_function(sim):
    if "LDPP-T" in sim.algorithm:
        return evaluate_objective_threshold
    elif "LDPP-GF" in sim.algorithm:
        return evaluate_objective_green_flow
    else:
        print(f'WRONG ALGORITHM {sim.algorithm}')
        

def determine_phases(sim, DET, optimal_phases, determined_phases, objective, pressure, count_optima, consensus, pressure_pp):
    
    # import necessary functions
    evaluate_obj = import_evaluation_function(sim)
    
    # Shuffle the order of update in each round to represent reality (where everything is decentralized) better
    shuffled_intersection_id = copy.copy(list(sim.intersections_data.keys()))
    random.shuffle(shuffled_intersection_id)
    
    # set with all newly determined intersections (necessary to know which intersections' objective to update)
    newly_det_intersections = set()
    
    # store all consensus values
    consensus = {}

    for intersection in shuffled_intersection_id:
        
        # if the intersection has already terminated, we skip it
        if intersection in determined_phases:
            continue
        
        # check if we have an agreement with all neighbours
        consensus[intersection], count_optima = check_agreement(sim, intersection, optimal_phases, DET)
        
        # if the intersection has found consensus with its neighbours, then its own phase and the phase of its
        # neigbours will be fixed
        if consensus[intersection]:
            for neighbour in sim.intersections_data[intersection]["neighbours"].union({intersection}):
                # if the neighbour (in the same round) has been determined as the smallest_objective (--> consensus of neighbour == False), we need to change again its phase, objective and pressure
                if neighbour in newly_det_intersections and consensus.get(neighbour, True) == False:
                    consensus_phase = np.argmax(optimal_phases[neighbour][neighbour])
                    determined_phases[neighbour] = {neighbour: optimal_phases[neighbour][neighbour]}
                    objective[neighbour][-1] = evaluate_obj(pressure_pp, sim, neighbour, optimal_phases)
                    pressure[neighbour][-1] = pressure_pp[neighbour][consensus_phase]
                
                # only change the phase if the neighbour has not terminated yet
                elif neighbour not in determined_phases:
                    DET[neighbour] = True
                    determined_phases[neighbour] = {neighbour: optimal_phases[neighbour][neighbour]}
                    newly_det_intersections.add(neighbour)

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
                # choose phase based on votes from neighbours
                neighbours_chosen_phase = np.argmax(count_optima)
                temp = np.zeros(len(count_optima))
                temp[neighbours_chosen_phase] = 1
                
                
                # need this structure to keep all variables consistent
                DET[intersection] = True
                newly_det_intersections.add(intersection)
                determined_phases[intersection] = {intersection: temp}
                objective[intersection][-1] = evaluate_obj(pressure_pp, sim, intersection, optimal_phases)
                pressure[intersection][-1] = pressure_pp[intersection][neighbours_chosen_phase]
                
                
    # Update the objectives of the neighboring intersections whose phases have just been determined
    update_objective(sim, objective, pressure, DET, pressure_pp, newly_det_intersections, optimal_phases)
                
                
    
                