from collections import defaultdict

class ObjectiveValueMetric:
    """ Records the objective value and pressure value averaged over all intersections per each Delta time step """
    
    def __init__(self):
        
        self.objective_values = defaultdict(list)
        self.pressure_values = defaultdict(list)
        
        
    def record_values(self, sim):
        
        for intersection in sim.intersections_data:
            self.objective_values[intersection].append(sim.perform["current_objective"][intersection])
            self.pressure_values[intersection].append(sim.perform["current_pressure"][intersection])
        
        
    def get_objective(self):
        # We take the average over all intersections
        # Transpose the data so that you iterate over time steps
        transposed_data_obj = zip(*self.objective_values.values())
        
        # Calculate the average for each time step
        averages_obj = [sum(time_step) / len(time_step) for time_step in transposed_data_obj]
        
        return averages_obj
    
    
    def get_pressure(self):
        # We take the average over all intersections
        # Transpose the data so that you iterate over time steps
        transposed_data_pres = zip(*self.pressure_values.values())

        # Calculate the average for each time step
        averages_pres = [sum(time_step) / len(time_step) for time_step in transposed_data_pres]
        
        return averages_pres