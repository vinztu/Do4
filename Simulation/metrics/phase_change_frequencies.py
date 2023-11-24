class PhaseChangeFrequencyMetric:
    """ Records with what frequency the phase changes. The maximal value would be after each Delta update and the minimal possible amount would be 0 (never changes tl) """
    
    def __init__(self, sim):
        self.number_of_phase_changes = {intersection: 0 for intersection in sim.intersections_data}
        
        # only used for comparison reasons within function below
        self.old_phase = {intersection: -1 for intersection in sim.intersections_data}
        
        
    def record_values(self, sim):
        
        for intersection in sim.intersections_data:
            
            if self.old_phase[intersection] != sim.perform["current_phase"][intersection]:
                self.number_of_phase_changes[intersection] += 1
                self.old_phase[intersection] = sim.perform["current_phase"][intersection]
                
                
    def get_phase_frequencies(self):
        # We take the average over all intersections
        average_frequency = sum(self.number_of_phase_changes.values()) / len(self.number_of_phase_changes)
        return average_frequency