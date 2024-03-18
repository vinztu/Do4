from collections import defaultdict
import numpy as np
import json
from .phase_definitions import phase_definitions

def initialize(sim, load_capacities):
    """ Initializes the simulation. This will read all information necessary from the roadnet file and store them into the Simulation class object 
    
    ...
    
    This function sets the following values:
    
    sim.lanes_data:
        key: lane_id
        values: [intersection_id, movement_id, upstream lanes, downstream lanes]
        
    sim.intersections_data:
        key: intersection_id
        values: {"inflow": [inflowing lanes], "outflow": [outflowing lanes], "neighbours": [all neighbouring intersections]
    
    """
    
    # get all lane id's in the entire network
    lane_ids = sim.engine.get_lane_vehicle_count().keys()
    
    
    def write_phases(sim):
        """
        create list to match format of roadnet file
        this implementation enables to set different phases for each intersection
        """
        
        phases_list = []
        default_time = 10 # default time is set to 10 sec
        
        for phase_lanes in sim.params["all_phases"]["normal_intersection"].values():
            
            phases_list.append({"time": default_time,
                                "availableRoadLinks": phase_lanes
                               }
                              )
        
        
        # This phase corresponds to the idle time (all tl are red)
        phases_list.append({"time": default_time,
                                "availableRoadLinks": []
                               }
                              )

        return phases_list
    
    
    def read_phases(intersection, sim, all_phase_definitions):
        """
        Read the phase definitions for an intersection and store it
        """
        
        phase_in_intersection = {}
        
        # read the phase from the predefined phase in the json file
        for index, phase in enumerate(intersection["trafficLight"]["lightphases"]):
            if phase["availableRoadLinks"] != []:
                phase_in_intersection[index] = phase["availableRoadLinks"]
            
        

        for key, phases in sim.params["all_phases"].items():
            if phases == phase_in_intersection:
                return key
            
            
        raise ValueError(f"Missing phase definition for {intersection['id']} with phase {phase_in_intersection} in phase_definition.py")
                
    
    
    def read_lane_names(intersection, sim):
        """ read all lane and intersection information from the roadnet file"""
        
        # stores information about intersections inflowing lanes
        intersections_inflow_data = set()
        
        # stores information about intersections outflowing lanes
        intersections_outflow_data = set()
        
         # initialize with a movement_id = 0
        movement_id = 0
        
        for roadLinks in intersection["roadLinks"]:
            
            # get start and end road id
            start_road = roadLinks["startRoad"]
            end_road = roadLinks["endRoad"]
            
            # only used temp
            previous_start_lane = -1
            
            for i in range(len(roadLinks["laneLinks"])):
                
                start_lane = start_road + "_" + str(roadLinks["laneLinks"][i]["startLaneIndex"])
                end_lane = end_road + "_" + str(roadLinks["laneLinks"][i]["endLaneIndex"])
                
                # in case there are multiple lanes going in the same direction (e.g. 7 lanes on 1 road)
                # They will receive the same movement_id
                if previous_start_lane != start_lane:
                    
                    # add inflow intersection to lane_data
                    sim.lanes_data[start_lane][0] = intersection["id"]
                    
                    # add inflow movement_id to lane_data
                    sim.lanes_data[start_lane][1] = movement_id
                    
                    # add one inflow lane to intersections_data
                    intersections_inflow_data.add(start_lane)
                    
                    # update the previous start lane
                    previous_start_lane = start_lane
                    
                
                # add the outflowing lane to the set for outflowing lanes from an intersection
                intersections_outflow_data.add(end_lane)
                
                # add the outflowing lane to the downstream lane of start_lane
                sim.lanes_data[start_lane][3].append(end_lane)
                
                # add the inflowing lane to the upstream lane of end_lane
                sim.lanes_data[end_lane][2].append(start_lane)
                
            # like this we will end up with the same numbering of movement as in the roadnet file
            movement_id += 1
        
        # combine the outflow and inflow data for an intersection
        sim.intersections_data[intersection["id"]] = {"inflow": intersections_inflow_data,
                                                      "outflow": intersections_outflow_data
                                                     }
                   
    
    
    def read_and_write_roadnet(sim, all_phase_definitions):
        """ Read the roadnet file and retrieve information"""
        
        # stores information about lanes: 
        # key: lane_id
        # values: {intersection_id, movement_id, upstream lanes, downstream lanes}
        sim.lanes_data = {lane: [None,None,[],[]] for lane in lane_ids}
        
        sim.intersections_data = {}
        
        
        with open(sim.dir_roadnet_file, "r") as jsonFile:
            data = json.load(jsonFile)
            
        for intersection in data["intersections"]:
            if (not intersection["virtual"]):
                
                if sim.write_phase_to_json:
                    # change phase of roadnet file for "intersection"
                    intersection["trafficLight"]["lightphases"] = write_phases(sim)
                    
                # read phase definitions for each intersection
                sim.params["intersection_phase"][intersection["id"]] = read_phases(intersection, sim, all_phase_definitions)
                    
                
                # read information about intersections and lanes from roadnet file for "intersection"
                read_lane_names(intersection, sim)
                
              
        # Write the modified data back to the file
        if sim.write_phase_to_json:
            with open(sim.dir_roadnet_file, "w") as jsonFile:
                json.dump(data, jsonFile, indent=4)
            
            
    
    def find_neighbouring_intersections(sim):
        """ For each intersection, find its neighbours"""
        
        for intersection in sim.intersections_data:
            
            # take only the first two integers of each lane to get the intersection
            potent_neighbours = set(map(lambda x: f"intersection_{x.split('_')[1]}_{x.split('_')[2]}", sim.intersections_data[intersection]["inflow"]))
            
            # filter out virtual neighbours
            sim.intersections_data[intersection]["neighbours"] = set(filter(lambda x: x in sim.intersections_data.keys(), potent_neighbours))


    def define_capacities(sim):
        """ Can be used to load capacities for individual lanes """
        
        if load_capacities:
            network = sim.params["road_network"]
            sim.params["capacity"] = json.load(open(f"Simulation_Results/{network}/capacities.json")) #(capacities for individual lanes)

        else:
            # previously sim.params["capacity"] has been an int defined in parameter_loader.py
            sim.params["capacity"] = {lane: sim.params["capacity"] for lane in sim.lanes_data}

    
    def LDPP_T_initialization(sim):
        """ Used to initialize an empty list for the penalty function in the LDPP algorithm """
        sim.params["constant_weight"] = {lane: 1 for lane in sim.lanes_data}
        sim.params["phase_history"] = {intersection: np.ones(sim.params["L"])*(-1) for intersection in sim.intersections_data}
        sim.params["num_consensus_iterations"] = []
        sim.params["saturation_flow"] = {lane: min(sim.params["capacity"][lane], sim.params["saturation_flow"]) for lane in sim.lanes_data}
    
        
    def LDPP_GF_initialization(sim):
        sim.params["num_consensus_iterations"] = []
        #sim.params["saturation_flow"] = {min(int(sim.params["capacity"][lane] * 0.5), sim.params["saturation_flow"]) for lane in sim.lanes_data}

    def Fixed_Time_initialization(sim):
        
        sim.params["previous_phase"] = {}
        for intersection in sim.intersections_data:
            phase_type = sim.params["intersection_phase"][intersection]
            
            sim.params["previous_phase"][intersection] = sim.params["fixed_time_params"][phase_type][0]
            
        
    def add_neighbours_manhattan(sim):
        sim.intersections_data["intersection_17_6"]["neighbours"].add("intersection_17_9")
        sim.intersections_data["intersection_16_9"]["neighbours"].add("intersection_16_6")
    
    
    # read all predefined phase definitions from phase_definitions.py (need to match those of the roadnet json file)
    all_phase_definitions = phase_definitions()
    
    # read from roadnet file and write back new phases  
    read_and_write_roadnet(sim, all_phase_definitions)
    
    # find neighbouring intersections
    find_neighbouring_intersections(sim)
    
    # bad solution here. only used for the Manhattan network!! (Add neighbours manually for intersection 17_6 and 16_9, since there is no incoming lane from neighbour 17_9 and 16_6 respectively)
    ######## and remove neighbours manually for intersection 17_9 and 16_6, since there is not outgoing lane to neighbour 17_6 and 16_9 respecively
    if sim.params["road_network"] == "Manhattan":
        add_neighbours_manhattan(sim)
    
    # define lane capacities (for all lanes)
    define_capacities(sim)
    
        
    if "LDPP-T" in sim.algorithm:
        LDPP_T_initialization(sim)
        
    if "LDPP-GF" in sim.algorithm:
        LDPP_GF_initialization(sim)
        
    if "Fixed-Time" in sim.algorithm:
        Fixed_Time_initialization(sim)
        