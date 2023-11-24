from collections import defaultdict

class NumWaitingMetric:
    """
    Records the average number of vehicles waiting over all intersection and lanes respectively
    It also records the top 10% of the most occupied lanes (this is done as the average over all lanes includes many empty lanes)
    """
    
    def __init__(self):
        
        self.num_wait_per_inter = defaultdict(list)
        self.num_wait_per_lane = []
        self.num_wait_per_lane_max = []
        
        
        
    def record_values(self, sim):
        
        # Get number of waiting vehicles on each lane.
        # Currently, vehicles with speed less than 0.1m/s are considered as waiting.
        waiting_vehicles = sim.engine.get_lane_waiting_vehicle_count()
        
        ### Per Intersection
        for intersection, inter_info in sim.intersections_data.items():
            
            # average number of cars on all inflowing lanes
            self.num_wait_per_inter[intersection].append(sum(waiting_vehicles[lane] for lane in inter_info["inflow"]))
            
        
        ### Per Lane
        sorted_lane_lenghts = sorted(waiting_vehicles.values(), reverse = True)
        len_list = len(sorted_lane_lenghts)
        
        if len_list != 0:
        
            # take the average from all lanes
            self.num_wait_per_lane.append(sum(sorted_lane_lenghts) / len(sorted_lane_lenghts))

            # take the top 10% of all lanes (but minimal 1)
            top_10 = max(1, int(0.1*len_list))
            self.num_wait_per_lane_max.append(sum(sorted_lane_lenghts[:top_10]) / len(sorted_lane_lenghts[:top_10]))
            
        else:
            self.num_wait_per_lane.append(0)
            self.num_wait_per_lane_max.append(0)
            
            
    def get_average_num_per_intersection(self):
        # We take the average over all intersections
        # Transpose the data so that you iterate over time steps
        transposed_data_intersection = zip(*self.num_wait_per_inter.values())

        # Calculate the average for each time step
        averages_intersection = [sum(time_step) / len(time_step) for time_step in transposed_data_intersection]

        return averages_intersection
        
    def get_average_number_per_lane(self):
        return self.num_wait_per_lane
        
    def get_max_number_per_lane(self):
        return self.num_wait_per_lane_max
        
        