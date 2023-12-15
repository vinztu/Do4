import copy
import numpy as np

def create_initial_values(arguments, intersection):
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
    lambda_ = {}
    
    # a list with all neighbouring intersections
    neighbouring_intersections = arguments["intersections_data"][intersection]["neighbours"].union({intersection})
    
    for neighbour in neighbouring_intersections:
        
        temp = {}
        
        neighbours_neighbouring_intersections = arguments["intersections_data"][neighbour]["neighbours"].union({neighbour})
        
        for neighbours_neighbour in neighbours_neighbouring_intersections:
            x_i = np.zeros(len(arguments["params"]["phases"]) , dtype=int)

            # set 1 random entry to 1
            idx = np.random.randint(len(arguments["params"]["phases"]))
            x_i[idx] = 1

            temp[neighbours_neighbour] = x_i.copy()
        
        # create a dict within a dict to match the format used later (it = 0)
        x[(0, neighbour)] =  temp.copy()
        lambda_[(0, neighbour)] = temp.copy()
    
    
    # the neighbouring intersections will define z_g for "their" component/intersection
    z_g = {(0, intersection): x_i.copy()}
        
    return x, lambda_, z_g



        