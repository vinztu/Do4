class ThroughputMetric:
    """ 
    Records the throughput of an intersection within a Delta time frame. The 
    throughput is defined as the number of cars that was able to pass through the intersection
    within Delta time steps
    """
    
    def __init__(self, sim):
        
        # store all vehicles that arrive within Delta time steps
        self.new_vehicles_set = {intersection: set() for intersection in sim.intersections_data}
        
        # store all vehicle id's that were at an intersection in the previous tl update
        self.old_vehicles_set = {intersection: set() for intersection in sim.intersections_data}
        
        # store the actual throughput within Delta time steps
        self.throughput = {intersection: [] for intersection in sim.intersections_data}
        

    def record_values(self, sim, current_time):
        
        vehicles_ids = sim.engine.get_vehicles()
        
        for vehicle in vehicles_ids:
            vehicle_info = sim.engine.get_vehicle_info(vehicle)
            
            # if the length of the info is 7, then the vehicle is NOT at an intersection
            # and if the lenght is 5, it is at an intersection
            if len(vehicle_info) == 5:

                # The outflowing lane gives the id of the current intersection
                inter_id = vehicle_info["drivable"].split("_")[-4:-2]
                current_intersection = f"intersection_{inter_id[0]}_{inter_id[1]}"
                
                # if not already present in the set, then add the vehicle id
                self.new_vehicles_set[current_intersection].add(vehicle)

                    
                    
        # here we take the average every Delta timesteps and reset the dict
        # note that this might increase the througput as we reset the time values
        if current_time % sim.params["delta"] == 0:
            
            for intersection in sim.intersections_data:
                
                # check which vehicles that were at the beginning at an intersection
                # are still there
                remaining_cars = self.old_vehicles_set[intersection].intersection(self.new_vehicles_set[intersection])
                
                # the difference is the amount of cars that was able to pass through the intersection
                # the average per time step is then divided by Delta
                self.throughput[intersection].append((len(self.old_vehicles_set[intersection]) - len(remaining_cars)) / sim.params["delta"])
                
                
                
            # set the old vehicles set to the new one and clear the new one
            self.old_vehicles_set = self.new_vehicles_set
            self.new_vehicles_set = {intersection: set() for intersection in sim.intersections_data}
                   
                    
    def get_througput(self):
        # we take the average over all intersections
        # Transpose the data so that you iterate over time steps
        transposed_data = zip(*self.throughput.values())

        # Calculate the average for each time step
        averages = [sum(time_step) / len(time_step) for time_step in transposed_data]


        return averages
                    
                
                
            
            
        