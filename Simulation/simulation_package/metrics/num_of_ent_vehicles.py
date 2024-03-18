class NumberVehicleEnteredMetric:
    """ Records the number of vehicles that entered the network during the whole simulation"""
    
    def __init__(self):
        # count the number of vehicles that entered at one point during the simulation
        self.number_of_vehicles = set()
        
        
    def record_values(self, sim):
        
        vehicles_id = sim.engine.get_vehicles(include_waiting=False)
        
        self.number_of_vehicles.update(vehicles_id)
                
            
    def get_number_of_vehicles(self):
        return len(self.number_of_vehicles)