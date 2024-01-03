from Simulation.algorithms.LDPP_helper.Greedy.optimize_objective import optimize_objective
from Simulation.algorithms.LDPP_helper.Greedy.check_agreement import check_agreement
from Simulation.algorithms.LDPP_helper.Greedy.determine_phases import determine_phases


def Greedy(sim, pressure_per_phase_id, arguments_id):
    """ Implements the Greedy loop to solve for the optimal phases
    
    Parameters
    -----------
    sim : Simulation
        Object of the Simulation Class
    
    pressure_pre_phase_id : ray.object
        Stores the pressure per phase for each intersection
    
    arguments_id : ray.object
        Stores data from sim (copy), since ray cannot serialize citylow objects
    
    
    Returns
    -----------
    x : dict
        Keys are intersection id's and values are np.arrays (one hot vector) where the optimal phase is active (=1)
    
    objective : dict
        Keys are intersection id's and values are a list of the objective value throughout the ADMM iterations for each intersection
    
    pressure : dict
        Keys are intersection id's and values are a list of the pressure value throughout the ADMM iterations for each intersection
    
    """
    
    ## initial values
    DET = {intersection: False for intersection in sim.intersections_data} # flag if intersection has terminated
    optimal_phases = {} # current optimal phase for each intersection (values are np.array)
    pressure = {intersection: [] for intersection in sim.intersections_data} # current pressure values for each intersection based on chosen phase
    objective = {intersection: [] for intersection in sim.intersections_data} 
    count_optima = {} # neighbour's choice of optimal phase decisions
    consensus = {} # flag if intersection has found consensus
    
    
    while sum(DET.values()) < len(DET):
        
        # each intersection optimizes its objective function
        optimize_objective(sim, pressure_per_phase_id, arguments_id, DET, optimal_phases, objective, pressure)
        
        # check wheter intersections have found consensus
        check_agreement(sim, arguments_id, optimal_phases, DET, consensus, count_optima)
        
        # determine phases based on agreement and objective value
        determine_phases(sim, DET, optimal_phases, objective, count_optima, consensus)
        
                
    return optimal_phases, objective, pressure