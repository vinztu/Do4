class AverageVehicleSpeedMetric:
    """ Records the average car speed over all vehicles"""
    
    def __init__(self):
        
        self.vehicles_speed = []
        
    
    def record_values(self, sim):
        
        average_vehicle_speed = sim.engine.get_vehicle_speed()
        
        # check if dict is empty
        if average_vehicle_speed:
            self.vehicles_speed.append(sum(average_vehicle_speed.values()) / len(average_vehicle_speed))
            
        # if there is no car
        else:
            self.vehicles_speed.append(0)
            
            
    def get_vehicles_speed(self):
        return self.vehicles_speed