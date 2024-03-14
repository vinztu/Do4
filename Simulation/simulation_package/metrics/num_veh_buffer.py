class NumVehiclesBuffer:
    """ Records the number of vehicles in the waiting buffer (waiting to enter the network)"""
    
    def __init__(self):
        
        self.num_waiting_vehicles = []
        
    
    def record_values(self, sim):
        
        all_vehicles = sim.engine.get_vehicles(include_waiting=True)
        
        current_waiting_veh = 0
        
        for vehicle in all_vehicles:
            if int(sim.engine.get_vehicle_info(vehicle)["running"]) == 0:
                current_waiting_veh += 1
        
        self.num_waiting_vehicles.append(current_waiting_veh)
            
            
    def get_num_waiting_buffer(self):
        return self.num_waiting_vehicles