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
        self.x[(0, intersection)] = x[(0, intersection)][intersection].copy()
        self.lambda_[(0, intersection)] = lambda_[(0, intersection)][intersection].copy()
        self.z[(it, intersection)] = z_g[(0, intersection)].copy()
        
    def set_lambda(self, tau, intersection, new_val):
        self.lambda_[(tau, intersection)] = new_val
        
    def get_lambda(self, tau, intersection):
        # returns a dict of intersection's lambda's at time tau (keys: neighbour's id and values: lambdas)
        return self.lambda_.get([(tau, intersection)], None)

    def set_x(self, tau, intersection, new_val):
        self.x[(tau, intersection)] = new_val

    def get_x(self, tau, intersection):
        # returns a dict of intersection's x_i's at time tau (keys: neighbour's id and values: x_i)
        return self.x.get((tau, intersection), None)
    
    def set_z_g(self, tau, intersection, new_val):
        # only update intersection's own z_g
        self.z[(tau, intersection)] = new_val[(it, intersection)]
        
    def get_z_g(self, tau, intersection):
        # returns a numpy list of len(phases)
        return self.z.get([(tau, intersection)], None)

