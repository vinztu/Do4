import numpy as np
import pandas as pd
from os import makedirs
from os.path import isdir

from .load_params import load_specific_params

from .computation_time import ComputationTimeMetric
from .objective import ObjectiveValueMetric
from .travel_time import TravelTimeMetric
from .throughput import ThroughputMetric
from .vehicle_speed import AverageVehicleSpeedMetric

from .num_instant_vehicles import NumVehiclesInstantaneous
from .num_veh_buffer import NumVehiclesBuffer
from .num_veh_wait import NumWaitingMetric
from .time_veh_wait import TimeWaitingMetric
from .num_of_ent_vehicles import NumberVehicleEnteredMetric
from .phase_change_frequencies import PhaseChangeFrequencyMetric


class Metrics:
    """ Initializes all Metrics classes and defines the two functions to retrieve information from the simulation
    The generate_report function is used to store and display these metrics"""
    
    
    def __init__(self, sim):
        self.computation_time = ComputationTimeMetric()
        self.objective_values = ObjectiveValueMetric()
        self.travel_time = TravelTimeMetric()
        self.throughput = ThroughputMetric(sim)
        self.vehicle_speed = AverageVehicleSpeedMetric()
        self.num_vehicles_instant = NumVehiclesInstantaneous()
        self.vehicle_in_buffer = NumVehiclesBuffer()
        self.num_waiting = NumWaitingMetric()
        self.time_waiting = TimeWaitingMetric(sim)
        self.num_ent_vehicle = NumberVehicleEnteredMetric()
        self.phase_change = PhaseChangeFrequencyMetric(sim)
        
        # number of simulation performance measurement points
        self.len_long_list = int(np.ceil(sim.params["sim_duration"]/sim.params["delta"]))
        
        
    def start_timer(self):
        # starts the computation timer for the controller
        self.computation_time.start_computation_timer()
        
        
    def stop_timer(self):
        # stops the computation timer for the controller
        self.computation_time.stop_computation_timer()
        
        
    def frequent_update(self, sim, current_time):
        """ This function will be called every time step"""
        
        # travel time not including the buffer
        self.travel_time.record_values(sim, current_time)
        
        # average numbers of vehicle per intersection per Delta
        self.throughput.record_values(sim, current_time)
        
        # records the average waiting time per vehicle, the maximal consecutive waiting time
        # and the number of times its speed falls below the threshold of 0.1m/s
        # (consecutive vs. not consecutive)
        self.time_waiting.record_values(sim)
        
        
        
        
    def infrequent_update(self, sim, current_time):
        """ This function will only be called after Delta time steps"""
        
        # objective and pressure per intersection
        self.objective_values.record_values(sim)
        
        # records the average vehicle speed
        self.vehicle_speed.record_values(sim)
        
        # records the number of waiting vehicles per lane and intersection
        self.num_waiting.record_values(sim)
    
        # counts the numver of vehicles that entered the network
        # and the number of stops per vehicle
        self.num_ent_vehicle.record_values(sim)
        
        # number of times the phase changes per intersection
        self.phase_change.record_values(sim)
        
        self.vehicle_in_buffer.record_values(sim)
        
        self.num_vehicles_instant.record_values(sim)
        
        
    def __extend_list(self, short_list):
        if isinstance(short_list, list):
            return short_list + [np.nan] * (self.len_long_list - len(short_list))
        elif isinstance(short_list, int) or isinstance(short_list, float):
            temp_list = [np.nan] * self.len_long_list
            temp_list[0] = short_list
            return temp_list
            
        print(type(short_lenght))
        print(type(self.len_long_list))
        return short_list + [np.nan] * (self.len_long_list - short_lenght)
        
        
    def generate_report(self, sim, current_round):
        """ This function generates a report by storing all performance measures into a file and displays them"""
        
        # create a time list
        time = np.arange(0, sim.params["sim_duration"], sim.params["delta"])
        
        # since this list is shorter, we need to pad it in order to fit it in the same df
        Waiting_Time_Per_Vehicle = self.__extend_list(self.time_waiting.get_average_waiting_time())
        Waiting_Time_Per_Vehicle_Max = self.__extend_list(self.time_waiting.get_max_waiting_time())
        Travel_time_w_Buffer = self.__extend_list(self.travel_time.get_travel_time_w_buffer(sim))
        Travel_time_wo_Buffer = self.__extend_list(self.travel_time.get_travel_time_wo_buffer())
        Number_of_Stops = self.__extend_list(self.time_waiting.get_average_num_of_stops())
        Num_ent_Vehicles = self.__extend_list(self.num_ent_vehicle.get_number_of_vehicles())
        Phase_Change_Frequency = self.__extend_list(self.phase_change.get_phase_frequencies())
        
        
        # Generate a dictionary and then save it as a dataframe
        performance = {
            "Time": time,
            "Computation Time": self.computation_time.get_comp_times(),
            "Objective Values": self.objective_values.get_objective(),
            "Pressure Values": self.objective_values.get_pressure(),
            "Travel Time w Buffer": Travel_time_w_Buffer,
            "Travel Time wo Buffer": Travel_time_wo_Buffer,
            "Throughput": self.throughput.get_througput(),
            "Vehicle Speed": self.vehicle_speed.get_vehicles_speed(),
            "Number of Vehicles Currently in Network": self.num_vehicles_instant.get_num_instant_vehicles(),
            "Number of Waiting Vehicles in Buffer": self.vehicle_in_buffer.get_num_waiting_buffer(),
            "Waiting Vehicles Per Intersection": self.num_waiting.get_average_num_per_intersection(),
            "Waiting Vehicles Per Lane": self.num_waiting.get_average_number_per_lane(),
            "Waiting Vehicles Per Lane Max": self.num_waiting.get_max_number_per_lane(),
            "Waiting Time Per Vehicle": Waiting_Time_Per_Vehicle,
            "Waiting Time Per Vehicle Max":  Waiting_Time_Per_Vehicle_Max,
            "Number of Stops": Number_of_Stops,
            "Number of Vehicles Entered the Network": Num_ent_Vehicles,
            "Phase Change Frequency": Phase_Change_Frequency
        }
        
        if "LDPP" in sim.algorithm:
            performance.update({"Number Consensus Iterations": sim.params["num_consensus_iterations"]})
        
        
        if isinstance(sim.params["saturation_flow"], dict) :
            sat_flow = max(sim.params["saturation_flow"].values())
        else:
            sat_flow = sim.params["saturation_flow"]
            
        
        # important meta information
        meta_information = {
            "delta": sim.params["delta"],
            "idle_time": sim.params["idle_time"],
            "sim_duration": sim.params["sim_duration"],
            "saturation_flow": sat_flow,
            "capacity": max(sim.params["capacity"].values())
        }
        important_info, specific_parameters = load_specific_params(sim)
        meta_information.update(specific_parameters)
        
        
            
        # Convert the dictionary to a DataFrame
        df = pd.DataFrame(performance)


        # if the directory does not exist, create a new one
        dir_name = f"Simulation_Results/{sim.params['road_network']}/Results/{sim.algorithm + '_' + '_'.join(str(info) for info in important_info)}"
        
        if not isdir(dir_name):
            makedirs(dir_name)
        
                
        # Save DataFrame to CSV without index
        with open(dir_name + "/" + str(current_round) + ".csv", 'w') as f:
            f.write(f"# {meta_information} \n")
            df.to_csv(f, index = False)