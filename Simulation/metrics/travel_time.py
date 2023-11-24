import numpy as np

class TravelTimeMetric:
    """ Records two variants for measuring the average travel time per vehicle
    One way is through the cityflow api while the other does not include the waiting buffer"""
    
    def __init__(self):
        
        # Can be requested directly by the cityflow api
        # includes cars waiting in the buffer
        self.travel_time_w_buffer = 0
        
        # does not include cars waiting in the buffer
        self.travel_time_wo_buffer = {}

        
    def record_values(self, sim, current_time):
        
        vehicles_ids = set(sim.engine.get_vehicles(include_waiting=False))
        
        # if a new vehicle arrives, put them into the dict
        temp = {flow: [current_time, np.nan] for flow in vehicles_ids if flow not in self.travel_time_wo_buffer}

        # if a vehicle is not anymore in the list, it has left the network
        for flow in self.travel_time_wo_buffer:
            if flow in vehicles_ids:
                self.travel_time_wo_buffer[flow][1] = current_time

        # add it to the dict     
        self.travel_time_wo_buffer.update(temp)
        
        
        
    def get_travel_time_w_buffer(self, sim):
        # use cityflow api to get the average travel time including buffer waiting time
        self.travel_time_w_buffer = sim.engine.get_average_travel_time()
        
        return self.travel_time_w_buffer
    
    
    def get_travel_time_wo_buffer(self):
        
        # take the average travel time over all vehicles
        # calculate the sum of distances, ignoring NaN values
        values_array = np.array([travel_end - travel_start for travel_start, travel_end in self.travel_time_wo_buffer.values() if not any(np.isnan(x) for x in [travel_start, travel_end])])

        # Calculate the sum of distances and divide by the count of non-NaN values
        average_travel_time_wo_buffer = np.nansum(values_array) / len(values_array)

        return average_travel_time_wo_buffer