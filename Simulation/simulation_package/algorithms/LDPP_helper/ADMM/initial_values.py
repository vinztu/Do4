import copy
import numpy as np

def create_initial_values(sim):
    """ Creates initial variables for the ADMM algorithm. It initializes all of them by
    a matrix that only contains one 1 per row
    We need the following keys per intersection:
    
    neighbouring_id: {neighbour: [phases] for neighbour in neighbours[neighbour]}
    
    and this for all neighbouring_id's that are neighbours to intersection (neighbour's neighbours)

    Parameters
    ----------
    sim : Simulation
        Object of the Simulation Class

    Returns
    -------
    x : dict
        A dictionary with intersection id's as keys and values are another dictionary. That dictionary has 
        neighbouring intersections as keys and binary phase variables as values
    
    lambda_ : dict
        A dictionary with intersection id's as keys and the corresponding value is another dictionary. That dictionary has 
        neighbouring intersections as keys and binary phase variables as values
        lambda_ are the dual variables
    """

        
    x = {}
    z = {}
    lambda_ = {}
    
    for intersection in sim.intersections_data:
        
        temp = {}
        
        neighbouring_intersections = sim.intersections_data[intersection]["neighbours"].union({intersection})
        
        for neighbour in neighbouring_intersections:
            
            neighbour_phase_type = sim.params["intersection_phase"][neighbour]
            
            # use floats here in case we use continuous z, since we need to add subtract x - z later (so both are floats)
            x_i = np.zeros(len(sim.params["all_phases"][neighbour_phase_type]) , dtype=np.float64)

            # set 1 random entry to 1
            idx = np.random.randint(len(sim.params["all_phases"][neighbour_phase_type]))
            x_i[idx] = 1

            temp[neighbour] = x_i.copy()
        
        # create a dict within a dict to match the format used later
        x[intersection] =  temp.copy()
        lambda_[intersection] = temp.copy()
        z[intersection] = x[intersection][intersection].copy()
        
    return x, z, lambda_



        