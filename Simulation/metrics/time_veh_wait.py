from collections import defaultdict

class TimeWaitingMetric:
    """ Records the average waiting time per vehicle, the maximal consecutive waiting time
    and the number of times its speed falls below the threshold of 0.1m/s (number of stops)
    
    """
    
    def __init__(self, sim):
        # vehicles with speed less than 0.1m/s are considered as waiting.
        self.WAITING_SPEED = 0.1
        
        # stores the waiting times for a vehicle during the whole simulation
        # NOT conescutive waiting time
        self.waiting_time = defaultdict(int)
        
        # counts the longest CONSECUTIVE waiting time
        self.waiting_time_longest = defaultdict(int)
        
        # stores the 10% longest CONSECUTIVE waiting times (over all vehicles)
        self.waiting_time_max = [("", 0) for _ in range(int(len(sim.lanes_data) * 0.1))]
        
        # stores the number of stops per vehicle
        self.number_of_stops = defaultdict(int)
        
        
        
    def record_values(self, sim):
        
        vehicle_speed_dict = sim.engine.get_vehicle_speed()

        for vehicle_id, vehicle_speed in vehicle_speed_dict.items():
            if vehicle_speed < self.WAITING_SPEED:
                
                # if the value is 0, then that vehicle just stopped in the last time step)
                if self.waiting_time_longest[vehicle_id] == 0:
                    self.number_of_stops[vehicle_id] += 1

                self.waiting_time[vehicle_id] += 1
                self.waiting_time_longest[vehicle_id] += 1

                # if the waiting time for vehicle id is longer than the smallest waiting time
                # in self.waiting_time_max, then replace it
                if self.waiting_time_longest[vehicle_id] > self.waiting_time_max[-1][1]:
                    self.waiting_time_max.pop()
                    self.waiting_time_max.append((vehicle_id, self.waiting_time_longest[vehicle_id]))
                    self.waiting_time_max.sort(key = lambda l: l[1], reverse = True)


            # if the vehicle is faster than WAITING_SPEED, then the consecutive period is over
            else:
                self.waiting_time_longest[vehicle_id] = 0
            
    
    def get_average_waiting_time(self):
        # We take the average waiting time per vehicle
        average_waiting_time = sum(self.waiting_time.values())/len(self.waiting_time)
        
        return average_waiting_time
    
    def get_max_waiting_time(self):
        max_waiting_time = sum(l[1] for l in self.waiting_time_max)/len(self.waiting_time_max)
        return max_waiting_time
    
    def get_average_num_of_stops(self):
        average_number_of_stops = sum(self.number_of_stops.values())/len(self.number_of_stops)
        return average_number_of_stops