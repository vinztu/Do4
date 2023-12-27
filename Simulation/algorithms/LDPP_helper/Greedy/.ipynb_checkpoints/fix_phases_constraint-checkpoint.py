import numpy as np

def fix_phases(m, x, DET, optimal_phases, agent_intersection, neighbouring_intersections):
    
    # if a phase of a neighbour is already determined, it cannot be changed
    for neighbour in neighbouring_intersections:
        
        if neighbour == agent_intersection:
            continue
        
        
        if DET[neighbour]:
            chosen_phase = np.argmax(optimal_phases[neighbour])
            m.addConstr(x[neighbour, chosen_phase] == 1)
            
    
