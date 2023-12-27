import ray
import numpy as np

from Simulation.algorithms.LDPP_helper.objective_evaluation import obj_eval
from Simulation.algorithms.LDPP_helper.Greedy.check_agreement import check_agreement
from Simulation.algorithms.LDPP_helper.Greedy.waiting_neighbours import waiting_neighbours_values, waiting_neighbours_DET_consensus, waiting_neighbours_DET, waiting_neighbours_terminated

from Simulation.algorithms.LDPP_helper.min_x_threshold import min_x as min_x_threshold
from Simulation.algorithms.LDPP_helper.min_x_green_flow import min_x as min_x_green_flow



def import_x_functions(arguments):
    if "LDPP-T" in arguments["algorithm"]:
        return min_x_threshold
    elif "LDPP-GF" in arguments["algorithm"]:
        return min_x_green_flow
    else:
        print(f'WRONG ALGORITHM {arguments["algorithm"]}')


def Greedy(global_state, intersection, arguments, pressure_per_phase, env):
    
    # a list with all neghbouring intersections
    neighbouring_intersections = arguments["intersections_data"][intersection]["neighbours"]
    
    # Initialize the variable DET = False for each neighbuor
    DET = {(-1,neighbour): False for neighbour in neighbouring_intersections}
    terminated = {neighbour: False for neighbour in neighbouring_intersections}
    optimal_phase = {}
    
    # import correct function
    min_x = import_x_functions(arguments)
    
    # set round counter
    it = 0
    
    # continue until DET-Flag (determined) will be set to 1
    while True:
        
        if it >= 20:
            print("MAX_ITEATION")
            break
        
        # optimize over intersection's objective function
        # it - 1 since in min_x, the new value will be saved as it + 1 (due to ADMM implementation)
        optimal_phase, objective, pressure = min_x(pressure_per_phase, arguments, env, intersection, it - 1, DET = DET, optimal_phase = optimal_phase)
        
        # share optimal phases
        ray.get(global_state.set_optimal_results.remote(it, intersection, optimal_phase, objective))
        
        # retrieve optimization results
        neighbours_optimal_phase, neighbours_objective = waiting_neighbours_values(global_state, arguments, it, intersection, terminated)
        optimal_phase.update(neighbours_optimal_phase)
        objective.update(neighbours_objective)
        
        print(optimal_phase)
        
        # check whether neighbours found consensus
        consensus, count_optima = check_agreement(arguments, intersection, optimal_phase, it, terminated, DET, global_state)
        
        if consensus:
            # found consensus for this intersection --> terminate and keep the phases and the neighbour's phase
            DET[(it, intersection)] = True # not really used, but for the concept
            determined_phase = np.argmax(optimal_phase[(it, intersection)])
            
            # if consensus, neighbours will terminate as well. Only in this case, set DET_Consensus = True in global dict
            ray.get([global_state.set_DET_consensus.remote(it, intersection, True), global_state.set_DET.remote(it, intersection, True), global_state.set_terminated.remote(intersection)])
            
            # set phases without it
            ray.get(global_state.set_phases_permanent.remote(intersection, it, optimal_phase))
            
            return [pressure], [objective[(it, intersection)]], determined_phase
        
        else:
            # set DET and DET_consensus = False
            ray.get(global_state.set_DET_consensus.remote(it, intersection, False))
            
            # check whether any neighbour has found consensus (dict {neighbour: neighbour's consens DET})
            neighbours_DET_consensus = waiting_neighbours_DET_consensus(global_state, arguments, it, intersection, terminated)
            
            # if any neighbour has found consensus, then we will terminate as well with that phase chosen
            if any(neighbours_DET_consensus.values()):
                # terminate and keep the phases as the neighbour found a consensus this intersection
                DET[(it, intersection)] = True # not really used, but for the concept
                determined_phase = np.argmax(optimal_phase[(it, intersection)])
                ray.get([global_state.set_DET.remote(it, intersection, True), global_state.set_terminated.remote(intersection)])
                # do not set DET_consensus = True, as only the neighbour has found consensus with all his neighbours
                # and we don't have to set the optimal result in the global dict anymore as they are the same as before calculated
                
                # set phases without it
                ray.get(global_state.set_phases_permanent.remote(intersection, it, optimal_phase))
            
                return [pressure], [objective[(it, intersection)]], determined_phase
            
            
            # retrieve neighbour's terminated values
            neighbours_terminated = waiting_neighbours_terminated(global_state, arguments, intersection)
            terminated.update(neighbours_terminated)
            
            # we initialize such that this intersection has the smallest objective value
            smallest_objective = True
            
            for neighbour in neighbouring_intersections:
                
                # check if the neighbouring intersection is still running
                # need to check both conditions as DET won't be updated anymore after the neighbour has terminated
                if not terminated[neighbour] and not DET[(it - 1, neighbour)]:
                
                    # check if current_intersection has the smallest pressure among its neighbours
                    if objective[(it,intersection)] > objective[(it, neighbour)]:
                        smallest_objective = False

                    # if the pressure is equal, the tie break is made based on the index given to each intersection
                    if objective[(it, intersection)] == objective[(it, neighbour)]:
                        if arguments["indices"][intersection] > arguments["indices"][neighbour]:
                            smallest_objective = False
                
                
            # if current intersection has the smallest pressure, then its phases will be determined
            # based on a majority vote
            if smallest_objective:
                DET[(it, intersection)] = True # not really used, but for the concept
                determined_phase = np.argmax(count_optima)
                pressure, objective = obj_eval(optimal_phase, pressure_per_phase, arguments, intersection, it)
                ray.get([global_state.set_DET.remote(it, intersection, True), global_state.set_terminated.remote(intersection)])
                
                # share optimal phases
                optimal_phase = {(it, intersection): count_optima}
                objective = {(it, intersection): objective}
                ray.get(global_state.set_optimal_results.remote(it, intersection, optimal_phase, objective))
                
                # set phases without it
                ray.get(global_state.set_phases_permanent.remote(intersection, it, optimal_phase))
                
                return [pressure], [objective[(it, intersection)]], determined_phase
            
            else:
                ray.get(global_state.set_DET.remote(it, intersection, False))
                
                
            # update which agent has terminated and which one is still running
            neighbours_DET = waiting_neighbours_DET(global_state, arguments, it, intersection, terminated)
            DET.update(neighbours_DET)
        
        # update the counter
        it += 1