import ray
import numpy as np
import copy



@ray.remote
class GlobalState:
    """ We define a global state to simulate communication among neighbours
    All nodes will use this same shared state
    """
    
    def __init__(self, arguments):
        
        self.x = {}
        self.lambda_ = {}
        self.z = {}
        
        
    def initialize_variables(self, arguments, x, lambda_, z_g, intersection):
        # initial values for tau = 0
        # only store the intersection's own variables (don't store (0, neighbour), since this will be stored by another agent)
        self.x[(0, intersection)] = x[(0, intersection)].copy() # dict
        self.lambda_[(0, intersection)] = lambda_[(0, intersection)].copy() # dict
        self.z[(0, intersection)] = z_g[(0, intersection)].copy() # list
        
    def set_lambda_(self, it, intersection, new_val):
        self.lambda_[(it, intersection)] = new_val
        
    def get_lambda_(self, it, intersection):
        # returns neighbours lambdas (list of len(phases))
        return self.lambda_.get((it, intersection), None)

    def set_x(self, it, intersection, new_val):
        self.x[(it, intersection)] = new_val

    def get_x(self, it, intersection):
        # returns neighbours x_i (list of len(phases))
        return self.x.get((it, intersection), None)
    
    def set_z_g(self, it, intersection, new_val):
        # only update intersection's own z_g
        self.z[(it, intersection)] = new_val[(it, intersection)]
        
    def get_z_g(self, it, intersection):
        # returns a numpy list of len(phases)
        return self.z.get((it, intersection), None)