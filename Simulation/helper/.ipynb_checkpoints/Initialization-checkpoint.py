from collections import defaultdict
import cityflow
import json

def initialize(sim):
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
        
        for phase_lanes in sim.params["phases"].values():
            
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
                   
    
    
    def read_and_write_roadnet(sim):
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
                # change phase of roadnet file for "intersection"
                intersection["trafficLight"]["lightphases"] = write_phases(sim)
                
                # read information about intersections and lanes from roadnet file for "intersection"
                read_lane_names(intersection, sim)
                
              
        # Write the modified data back to the file
        with open(sim.dir_roadnet_file, "w") as jsonFile:
            json.dump(data, jsonFile, indent=4)
            
            
    
    def find_neighbouring_intersections(sim):
        """for each intersection, find its neighbours"""
        
        for intersection in sim.intersections_data.keys():
            
            # take only the first two integers of each lane to get the intersection
            potent_neighbours = set(map(lambda x: f"intersection_{x.split('_')[1]}_{x.split('_')[2]}", sim.intersections_data[intersection]["inflow"]))
            
            # filter out virtual neighbours
            sim.intersections_data[intersection]["neighbours"] = set(filter(lambda x: x in sim.intersections_data.keys(), potent_neighbours))
            
            
    
       
    # read from roadnet file and write back new phases  
    read_and_write_roadnet(sim)
    
    # find neighbouring intersections
    find_neighbouring_intersections(sim)
    
    
