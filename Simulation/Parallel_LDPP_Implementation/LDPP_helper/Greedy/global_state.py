import ray

@ray.remote
class GlobalState:
    """ We define a global state to simulate communication among neighbours
    All nodes will use this same shared state
    """
    
    def __init__(self, arguments):
        
        # keeps track of the intersections that terminated due to consensus (--> affects neighbourin intersections)
        self.DET_consensus = {(0, intersection): False for intersection in arguments["intersections_data"]}
        
        # keeps track of the intersections that terminated (consensus or smallest objective)
        # serves as well as a "ready" signal (intersection as updated its values)
        self.DET = {(0, intersection): False for intersection in arguments["intersections_data"]}
        
        # boolean value for each intersection that is True if the intersection has terminated
        # same as DET, but with the difference that we do not have "it-number" in the key --> since intersection won't update self.DET anymore once it has terminated
        # self.DET still necessary since we need to make sure (in case the intersection is still running) that is has already updated its status --> need "it-number"
        self.terminated = {intersection: False for intersection in arguments["intersections_data"]}
        
        # saves optimal phases for each intersections (used to "communicate")
        self.optimal_phase = {}
        
        # saves the optimal objective value for each intersections (used to "communicate")
        self.objective = {}
        
        # indicates whether the intersection has changed its optimal phase after its initial optimization (i.e. in the voting stage)
        # do not need the "it" key here, as the intersections gets "synchronized" by previous global.get calls
        self.changed_phase = {intersection: False for intersection in arguments["intersections_data"]}
        
    def set_optimal_results(self, it, intersection, optimal_phase, objective):
        self.optimal_phase[(it, intersection)] = optimal_phase[(it, intersection)]
        self.objective[(it, intersection)] = objective[(it, intersection)]
        
    def get_optimal_values(self, it, intersection):
        return self.optimal_phase.get((it, intersection), None), self.objective.get((it, intersection), None)
    
    def set_phases_permanent(self, intersection, it, optimal_phase):
        self.optimal_phase[intersection] = optimal_phase[it, intersection]
        
    def set_DET_consensus(self, it, intersection, boolean):
        self.DET_consensus[(it, intersection)] = boolean
        
    def get_DET_consensus(self, it, intersection):
        return self.DET_consensus.get((it, intersection), None)
        
    def set_DET(self, it, intersection, boolean):
        self.DET[(it, intersection)] = boolean
    
    def get_DET(self, it, intersection):
        return self.DET.get((it, intersection), None)
                                      
    def set_terminated(self, intersection):
        self.terminated[intersection] = True
        
    def get_terminated(self, intersection):
        return self.terminated.get(intersection)
        
    def set_changed_phase(self, intersection, value):
        self.changed_phase[intersection] = value
    
    def get_changed_phase(self, intersection):
        return self.changed_phase[intersection]
                                    
        
        
        