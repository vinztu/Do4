import json
import cityflow

def read_roadmap(Road_map_Json):
    """Returns all roads, where each road is connected
    to a virtual intersection (a intersection not inside)

    Args:
        Road_map_Json (string): directory for the roadmap.json file 

    Returns:
        list: All roads adjacent to a virtual intersection
    """
    # Opening JSON file
    Json_file = Road_map_Json
    f = open(Json_file)
      
    # returns JSON object as 
    # a dictionary
    data = json.load(f)
      
    # define 2 empty lists for the for loop
    virtual_intersections = set()
    road_adj_virt_intersection_IN = set()
    road_adj_virt_intersection_OUT = set()
    
    # save the outflowing road that is adjacent to the inflowing road 
    road_adj_to_IN = {}
    # Input road and adjacent outflow road
    Mapping_IN_to_OUT = {0:2, 1:3, 2:0, 3:1}
    
    # Iterating through the json
    for intersection in data["intersections"]:
        if intersection["virtual"] == True:
            virtual_intersections.add(intersection["id"])
    
    for road in data["roads"]:
        if road["startIntersection"] in virtual_intersections:
            road_adj_virt_intersection_IN.add(road["id"])
            
            end_intersection = road["endIntersection"].split("_")
            road_adj_to_IN[road["id"]] = "road_" + "_".join(end_intersection[-2:]) + "_" + str(Mapping_IN_to_OUT[int(road["id"][-1])])
            
        if road["endIntersection"] in virtual_intersections:
            road_adj_virt_intersection_OUT.add(road["id"])
        
    
    # config file
    config_file = Road_map_Json.rstrip("roadnet.json") + "config.json"
    
    # start the engine to later retrieve all lane id's
    engine = cityflow.Engine(config_file, 1)
    
    # get all lane id's in the entire network
    lane_ids = engine.get_lane_vehicle_count().keys()
    
    roads_INSIDE = {road[:-2] for road in lane_ids if road[:-2] not in road_adj_virt_intersection_IN.union(road_adj_virt_intersection_OUT)}
    
    
    # Closing file
    f.close()
    
    return road_adj_virt_intersection_IN, road_adj_virt_intersection_OUT, road_adj_to_IN, roads_INSIDE