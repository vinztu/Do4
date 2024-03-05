import random
from itertools import product
import numpy as np


def generate_valid_combinations(road_in, road_out, road_adj_to_IN, percentage, inside_roads = False):
    
    # create all combinations of inflowing and outflowing
    all_combinations = list(product(road_in, road_out))
    
    if not inside_roads:
        # filter "not valid" (adjacent) roads
        all_combinations[:] = [comb for comb in all_combinations if road_adj_to_IN[comb[0]] != comb[1]]
    
    # take only a percentage of the remaining valid options
    filtered_combinations = random.sample(all_combinations, round(len(all_combinations) * percentage))
    
    return filtered_combinations


def generate_predefined_routes(parameters, roads):
    all_combinations = []
    
    main_roads = parameters[roads]
    
    for combinations in main_roads.values():
        all_combinations.append(combinations)
        
    return all_combinations


def generate_inside_combinations(roads_INSIDE, percentage):
    all_combinations = list(product(roads_INSIDE, roads_INSIDE))
    
    # only consider combinations that are separated by at least 10 intersections vertically and 1 intersections horizontally
    all_combinations[:] = [comb for comb in all_combinations
                           if (np.abs(int(comb[0].split("_")[1]) - int(comb[1].split("_")[1])) > 5) and (np.abs(int(comb[0].split("_")[2]) - int(comb[1].split("_")[2])) > 7)
                           and (np.abs(int(comb[0].split("_")[1]) - int(comb[1].split("_")[1])) < 10)
                          and (comb[0] != comb[1])]
    
    # take only a percentage of the remaining valid options
    filtered_combinations = random.sample(all_combinations, round(len(all_combinations) * percentage))
    
    return filtered_combinations


def generate_horizontal_combinations(roads_INSIDE, percentage):
    all_combinations = list(product(roads_INSIDE, roads_INSIDE))
    
    # only consider combinations that are separated by at least and 3 intersections horizontally
    all_combinations[:] = [comb for comb in all_combinations
                           if ((int(comb[0].split("_")[3]) == 1) or (int(comb[0].split("_")[3]) == 3)) and ((int(comb[1].split("_")[3]) == 1) or (int(comb[1].split("_")[3]) == 3))
                           and (np.abs(int(comb[0].split("_")[2]) - int(comb[1].split("_")[2])) >= 6) and (np.abs(int(comb[0].split("_")[1]) - int(comb[1].split("_")[1])) >= 6)
                           and (comb[0] != comb[1])]
    
    # take only a percentage of the remaining valid options
    filtered_combinations = random.sample(all_combinations, round(len(all_combinations) * percentage))
    
    return filtered_combinations
    

def generate_random_routes(roads_IN, roads_OUT, roads_INSIDE, road_adj_to_IN, parameters):
    """Generate random combinations of roads. The amount of trafic can be specified

    Args:
        roads_IN (set[str]): set of all inflowing roads adjacent to a virtual intersection
        roads_OUT (set[str]): set of all outflowing roads adjacent to a virtual intersection
        road_adj_to_IN (set[str]): set with all adjacent roads
        parameters (dict): parameters with demand ratio

    Returns:
        dict: dict of all combinations
    """
    filtered_combinations_1 = generate_valid_combinations(roads_IN, roads_OUT, road_adj_to_IN, parameters["traffic_ratio_out"])
    
    filtered_combinations_2 = generate_inside_combinations(roads_INSIDE, parameters["traffic_ratio_in"])
    
    
    return {"all": filtered_combinations_1 + filtered_combinations_2}



def check_flow(flow_dict):
    
    temp_1 = {desc: 0 for desc in flow_dict}
    temp_2 = {}
    
    for desc, values in flow_dict.items():
        
        temp_2[desc] = len(values)
        
        for [inflow, *_, outflow] in values:
            if (int(inflow.split("_")[2]) <= 6 and int(outflow.split("_")[2]) >= 9) or (int(inflow.split("_")[2]) >= 9 and int(outflow.split("_")[2]) <= 6):
                temp_1[desc] += 1
                
    new = {}
    for desc in temp_1:
        new[desc] = f"{temp_1[desc]}/{temp_2[desc]}"
        
    print("How many horizontal flows per category exist")    
    print(new)
    print()



def generate_specific_routes(roads_IN, roads_OUT, road_adj_to_IN, roads_INSIDE, parameters):
    """Generate combinations of roads. The amount of trafic is specified per main and side roads

    Args:
        roads_IN (set[str]): set of all inflowing roads adjacent to a virtual intersection
        roads_OUT (set[str]): set of all outflowing roads adjacent to a virtual intersection
        road_adj_to_IN (set[str]): set with all adjacent roads
        parameters (dict): parameters with demand ratio

    Returns:
        dict: dict of all combinations
    """
    
    
    main_roads_IN = []
    main_roads_OUT = []
    for od_pair in parameters["all_main_roads"].values():
        for combination in od_pair.values():
            main_roads_IN.append(combination[0])
            main_roads_OUT.append(combination[1])
    
    
    # find all side inflowing and outflowing roads
    side_roads_IN = [road for road in parameters["side_roads"] if road in roads_IN]
    side_roads_OUT = parameters["side_roads"].difference(side_roads_IN)
    
    ### create combinations according to specifications
    # just creates lists out of the predefined dict
    main_to_main = {}
    for proportion in parameters["proportions"]:
        origin = proportion.split("_")[0]
        origin_roads = [road[0] for road in parameters["all_main_roads"][origin].values()]
                            
        destination = proportion.split("_")[1]
        # choose the correct dict with the outflowing lanes
        destination_map = parameters["mapping"][destination]
        destination_roads = [road[1] for road in parameters["all_main_roads"][destination_map].values()]
        
        # percentage of all possible combinations
        ratio = parameters["proportions"][proportion][1]
        
        #############################################################print(origin, origin_roads, destination, destination_roads)
        main_to_main[proportion] = generate_valid_combinations(origin_roads, destination_roads, road_adj_to_IN, ratio)

          
    # main to side roads
    main_to_side = generate_valid_combinations(main_roads_IN, side_roads_OUT, road_adj_to_IN, parameters["mts"]["ratio"])

    # side to side roads
    side_to_side = generate_valid_combinations(side_roads_IN, side_roads_OUT, road_adj_to_IN, parameters["sts"]["ratio"])
    
    # side to main roads
    side_to_main = generate_valid_combinations(side_roads_IN, main_roads_OUT, road_adj_to_IN, parameters["stm"]["ratio"])
                              
    # inside to inside roads
    inside_to_inside = generate_inside_combinations(roads_INSIDE, parameters["iti"]["ratio"])
    
    # horizontal traffic
    horizontal_traffic = generate_horizontal_combinations(roads_INSIDE, parameters["horizontal"]["ratio"])

    all_combinations = {
        **main_to_main,
        "mts": main_to_side,
        "sts": side_to_side,
        "stm": side_to_main,
        "iti": inside_to_inside,
        "horizontal": horizontal_traffic,
    }
    
    check_flow(all_combinations)
    
    
    return all_combinations