class NumberVehicleEnteredMetric:
    """ Records the number of vehicles that entered the network during the whole simulation"""
    
    def __init__(self):
        # count the number of vehicles that entered at one point during the simulation
        self.number_of_vehicles = set()
        
        # record the number of running vehicles at each time point
        self.vehicle_count = []
        
        
    def record_values(self, sim):
        
        vehicles_id = sim.engine.get_vehicles(include_waiting=False)
        
        self.number_of_vehicles.update(vehicles_id)
        
        self.vehicle_count.append(sim.engine.get_vehicle_count())
                
            
    def get_number_of_vehicles(self):
        return len(self.number_of_vehicles)