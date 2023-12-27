import numpy as np

def fix_phases(m, x, it, DET, optimal_phase, agent_intersection, neighbouring_intersections):
    
    # if a phase of a neighbour is already determined, it cannot be changed
    for neighbour in neighbouring_intersections:
        
        if neighbour == agent_intersection:
            continue
        
        # it, as we already pass it - 1 in the min_x function (if intersection was determined in previous round)
        det_value = DET.get((it, neighbour), True)
        
        if det_value:

            #print(f"intersection {agent_intersection} neighbour {neighbour}, DET {DET} opt {optimal_phase}")

            chosen_phase = np.argmax(optimal_phase[(it,neighbour)])
            m.addConstr(x[neighbour, chosen_phase] == 1)
            
        elif det_value == None:
            
            #print(f"intersection {agent_intersection} neighbour {neighbour}, DET {DET} opt {optimal_phase}")
            
            chosen_phase = np.argmax(optimal_phase[neighbour])
            m.addConstr(x[neighbour, chosen_phase] == 1)
