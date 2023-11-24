import time

class ComputationTimeMetric:
    """ Records the computational needed for one iteration of the controller"""
    
    def __init__(self):
        self.comp_times = []

    def start_computation_timer(self):
        self.comp_times.append(time.time())
        
        
    def stop_computation_timer(self):
        self.comp_times[-1] = time.time() - self.comp_times[-1]

        
    def get_comp_times(self):
        return self.comp_times