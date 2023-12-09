import random
from itertools import product


def generate_valid_combinations(road_in, road_out, road_adj_to_IN, percentage):
    
    # create all combinations of inflowing and outflowing
    all_combinations = list(product(road_in, road_out))
    
    # filter "not valid" (adjacent) roads
    all_combinations[:] = [comb for comb in all_combinations if road_adj_to_IN[comb[0]] != comb[1]]
    
    # take only a percentage of the remaining valid options
    filtered_combinations = random.sample(all_combinations, round(len(all_combinations) * percentage))
    
    return filtered_combinations
    
    

def generate_random_routes(roads_IN, roads_OUT, road_adj_to_IN, parameters):
    """Generate random combinations of roads. The amount of trafic can be specified

    Args:
        roads_IN (set[str]): set of all inflowing roads adjacent to a virtual intersection
        roads_OUT (set[str]): set of all outflowing roads adjacent to a virtual intersection
        road_adj_to_IN (set[str]): set with all adjacent roads
        parameters (dict): parameters with demand ratio

    Returns:
        dict: dict of all combinations
    """
    filtered_combinations = generate_valid_combinations(roads_IN, roads_OUT, road_adj_to_IN, parameters["traffic_ratio"])
    
    return {"all": filtered_combinations}



def generate_specific_routes(roads_IN, roads_OUT, road_adj_to_IN, parameters):
    """Generate combinations of roads. The amount of trafic is specified per main and side roads

    Args:
        roads_IN (set[str]): set of all inflowing roads adjacent to a virtual intersection
        roads_OUT (set[str]): set of all outflowing roads adjacent to a virtual intersection
        road_adj_to_IN (set[str]): set with all adjacent roads
        parameters (dict): parameters with demand ratio

    Returns:
        dict: dict of all combinations
    """
    
    # find all main inflowing and outflowing roads 
    main_roads_IN = [road for road in parameters["main_roads"] if road in roads_IN]
    main_roads_OUT = parameters["main_roads"].difference(main_roads_IN)
    
    # find all side inflowing and outflowing roads
    side_roads_IN = [road for road in parameters["side_roads"] if road in roads_IN]
    side_roads_OUT = parameters["side_roads"].difference(side_roads_IN)
    
    ### create combinations according to specifications
    
    # main to main roads
    main_to_main = generate_valid_combinations(main_roads_IN, main_roads_OUT, road_adj_to_IN, parameters["mtm"]["ratio"])
    
    # main to side roads
    main_to_side = generate_valid_combinations(main_roads_IN, side_roads_OUT, road_adj_to_IN, parameters["mts"]["ratio"])
    
    # side to side roads
    side_to_side = generate_valid_combinations(side_roads_IN, side_roads_OUT, road_adj_to_IN, parameters["sts"]["ratio"])
    
    # side to main roads
    side_to_main = generate_valid_combinations(side_roads_IN, main_roads_OUT, road_adj_to_IN, parameters["stm"]["ratio"])
    
    
    all_combinations = {
        "mtm": main_to_main,
        "mts": main_to_side,
        "sts": side_to_side,
        "stm": side_to_main
    }
    
    return all_combinations