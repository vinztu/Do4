class PhaseChangeFrequencyMetric:
    """ Records with what frequency the phase changes. The maximal value would be after each Delta update and the minimal possible amount would be 0 (never changes tl) """
    
    def __init__(self, sim):
        self.number_of_phase_changes = {intersection: 0 for intersection in sim.intersections_data}
        
        # only used for comparison reasons within function below
        self.old_phase = {intersection: -1 for intersection in sim.intersections_data}

        # count number of possible updates
        self.counter = 0
        
        
    def record_values(self, sim):

        self.counter += 1
        
        for intersection in sim.intersections_data:
            
            if self.old_phase[intersection] != sim.perform["current_phase"][intersection]:
                self.number_of_phase_changes[intersection] += 1
                self.old_phase[intersection] = sim.perform["current_phase"][intersection]
                
                
    def get_phase_frequencies(self):
        # We take the average over all intersections and divide by the maximal amount of possible updates
        # The value will then be between [0,1]
        average_frequency = sum(self.number_of_phase_changes.values()) / (len(self.number_of_phase_changes) * self.counter)
        return average_frequency