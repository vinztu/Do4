class ThroughputMetric:
    """ 
    Records the throughput of an intersection within a Delta time frame. The 
    throughput is defined as the number of cars that was able to pass through the intersection
    within Delta time steps
    
    It is calculated as follows:
    old_vehicles_set stores the vehicle id's that were present on an intersection in the previous time step
    new_vehicles_set stores all veicle id's that are present in the new time step
    The vehicles that were present in old_vehicles_set but not in new_vehicles_set have left the intersection --> cars_passed += 1
    """
    
    def __init__(self, sim):
        
        # store all vehicles that arrive within Delta time steps
        self.new_vehicles_set = {intersection: set() for intersection in sim.intersections_data}
        
        # store all vehicle id's that were at an intersection in the previous tl update
        self.old_vehicles_set = {intersection: set() for intersection in sim.intersections_data}
        
        # the amount of cars left in delta time
        self.cars_passed = {intersection: 0 for intersection in sim.intersections_data}
        
        # store the actual throughput within Delta time steps
        self.throughput = {intersection: [] for intersection in sim.intersections_data}
        

    def record_values(self, sim, current_time):
        
        vehicles_ids = sim.engine.get_vehicles()
        
        # reset the new set
        self.new_vehicles_set = {intersection: set() for intersection in sim.intersections_data}
        
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

        
        for intersection in sim.intersections_data:
            # check set with previous round to see if some cars left the intersection
            remaining_cars = self.old_vehicles_set[intersection].intersection(self.new_vehicles_set[intersection])

            # the ones that are not here anymore, left the intersection
            self.cars_passed[intersection] += len(self.old_vehicles_set[intersection]) - len(remaining_cars)
        
        # update the "old" set
        self.old_vehicles_set = self.new_vehicles_set
        
        
        # here we take the average every Delta timesteps and reset the dict
        if current_time % sim.params["delta"] == 0:
            
            for intersection in sim.intersections_data:
                
                # the average per time step is then divided by Delta
                self.throughput[intersection].append(self.cars_passed[intersection] / sim.params["delta"])
                
                # reset the counter to 0
                self.cars_passed[intersection] = 0
                
                   
                    
    def get_througput(self):
        # we take the average over all intersections
        # Transpose the data so that you iterate over time steps
        transposed_data = zip(*self.throughput.values())

        # Calculate the average for each time step
        averages = [sum(time_step) / len(time_step) for time_step in transposed_data]


        return averages
                    
                
                
            
            
        