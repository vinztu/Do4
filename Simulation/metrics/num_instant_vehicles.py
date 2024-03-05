class NumVehiclesInstantaneous:
    """ Records the number of vehicles that are inside the network"""
    
    def __init__(self):
        
        self.num_current_vehicles = []
        
    
    def record_values(self, sim):
        
        self.num_current_vehicles.append(len(sim.engine.get_vehicles(include_waiting=False)))
            
            
    def get_num_instant_vehicles(self):
        return self.num_current_vehicles