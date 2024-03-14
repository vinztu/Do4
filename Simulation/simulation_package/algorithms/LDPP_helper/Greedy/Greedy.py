from .optimize_objective import optimize_objective
from .determine_phases import determine_phases

import ray
import numpy as np

from pprint import pprint

def Greedy(sim, pressure_pp, arguments_id):
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
    
    # put it in the shared memory
    pressure_per_phase_id = ray.put(pressure_pp)
    
    ## initial values
    DET = {intersection: False for intersection in sim.intersections_data} # flag if intersection has terminated
    optimal_phases = {} # current optimal phase for each intersection (values are np.array)
    determined_phases = {} # store all confirmed phases (slightly different to optimal phases --> during update, determined phases
    
    pressure = {intersection: [] for intersection in sim.intersections_data} # current pressure values for each intersection based on chosen phase
    objective = {intersection: [] for intersection in sim.intersections_data} 
    
    count_optima = {} # neighbour's choice of optimal phase decisions
    consensus = {} # flag if intersection has found consensus
    
    tau = 0
    
    while sum(DET.values()) < len(DET):
        
        # increase the rounds needed for consensus
        tau += 1
        
        # each intersection optimizes its objective function
        optimize_objective(sim, pressure_per_phase_id, arguments_id, DET, optimal_phases, determined_phases, objective, pressure)
        
        # determine phases based on agreement and objective value
        determine_phases(sim, DET, optimal_phases, determined_phases, objective, pressure, count_optima, consensus, pressure_pp)
        
        
    sim.params["num_consensus_iterations"].append(tau)
    
    return determined_phases, objective, pressure