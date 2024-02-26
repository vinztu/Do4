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
                           and (np.abs(int(comb[0].split("_")[2]) - int(comb[1].split("_")[2])) > 6) and (comb[0] != comb[1])]
    
    # take only a percentage of the remaining valid options
    filtered_combinations = random.sample(all_combinations, round(len(all_combinations) * percentage))
    
    return filtered_combinations


def generate_left_combinations(roads_INSIDE_IN, roads_INSIDE_OUT, percentage):
    all_combinations = list(product(roads_INSIDE_IN, roads_INSIDE_OUT))
    
    # only consider combinations that are separated by at least and 1 intersections horizontally
    all_combinations[:] = [comb for comb in all_combinations
                           if ((int(comb[0].split("_")[3]) == 1) or (int(comb[0].split("_")[3]) == 3)) and ((int(comb[0].split("_")[1]) < 8) and (int(comb[1].split("_")[1]) < 8))
                          and (np.abs(int(comb[0].split("_")[2]) - int(comb[1].split("_")[2])) > 6) and (comb[0] != comb[1])]
    
    # take only a percentage of the remaining valid options
    filtered_combinations = random.sample(all_combinations, round(len(all_combinations) * percentage))
    
    return filtered_combinations


def generate_bottom_combinations(roads_INSIDE_IN, roads_INSIDE_OUT, percentage):
    all_combinations = list(product(roads_INSIDE_IN, roads_INSIDE_OUT))
    
    # only consider combinations that are separated by at least and 1 intersections horizontally
    all_combinations[:] = [comb for comb in all_combinations
                           if ((int(comb[0].split("_")[3]) == 1) or (int(comb[0].split("_")[3]) == 3)) and ((int(comb[0].split("_")[2]) <= 6) and (int(comb[1].split("_")[2]) < 6))
                           and (int(comb[0].split("_")[1]) >= 10) and ((int(comb[1].split("_")[1]) <= 15) or (int(comb[1].split("_")[1]) >= 18))
                           and (np.abs(int(comb[0].split("_")[1]) - int(comb[1].split("_")[1])) > 5) and (np.abs(int(comb[0].split("_")[1]) - int(comb[1].split("_")[1])) < 12)
                           and (np.abs(int(comb[0].split("_")[2]) - int(comb[1].split("_")[2])) > 2) 
                           and (comb[0] != comb[1])]
                            # 
        
    # take only a percentage of the remaining valid options
    filtered_combinations = random.sample(all_combinations, round(len(all_combinations) * percentage))
    
    return filtered_combinations


def generate_only_bottom_straight_combinations(roads_INSIDE_IN, roads_INSIDE_OUT, percentage):
    all_combinations = list(product(roads_INSIDE_IN, roads_INSIDE_OUT))
    
    # only consider combinations that are separated by at least and 1 intersections horizontally
    all_combinations[:] = [comb for comb in all_combinations
                           if (((int(comb[0].split("_")[3]) == 1) and (int(comb[1].split("_")[3]) == 1)) or ((int(comb[0].split("_")[3]) == 3) and (int(comb[1].split("_")[3]) == 3)))
                           and ((int(comb[0].split("_")[2]) <= 6) and (int(comb[1].split("_")[2]) < 6))
                           and (int(comb[0].split("_")[1]) == int(comb[1].split("_")[1])) and (int(comb[1].split("_")[1]) > 9)
                           and (np.abs(int(comb[0].split("_")[2]) - int(comb[1].split("_")[2])) >= 5)
                           and (comb[0] != comb[1])]
                            # 
        
    # take only a percentage of the remaining valid options
    filtered_combinations = random.sample(all_combinations, round(len(all_combinations) * percentage))
    
    return filtered_combinations

def generate_top_combinations(roads_INSIDE_IN, roads_INSIDE_OUT, percentage):
    all_combinations = list(product(roads_INSIDE_IN, roads_INSIDE_OUT))
    
    # only consider combinations that are separated by at least and 1 intersections horizontally
    all_combinations[:] = [comb for comb in all_combinations
                           if ((int(comb[0].split("_")[3]) == 1) or (int(comb[0].split("_")[3]) == 3)) and ((int(comb[1].split("_")[3]) == 1) or int(comb[1].split("_")[3]) == 3)
                           and (np.abs(int(comb[0].split("_")[1]) - int(comb[1].split("_")[1])) > 5) and (np.abs(int(comb[0].split("_")[1]) - int(comb[1].split("_")[1])) < 9)
                           and (np.abs(int(comb[0].split("_")[2]) - int(comb[1].split("_")[2])) > 2)
                           and (int(comb[0].split("_")[2]) >= 9) and (int(comb[1].split("_")[2]) >= 9)
                           and (comb[0] != comb[1])]
                            # and (int(comb[0].split("_")[2]) == 9) and (int(comb[1].split("_")[2]) == 11) 
        
    # take only a percentage of the remaining valid options
    filtered_combinations = random.sample(all_combinations, round(len(all_combinations) * percentage))
    
    return filtered_combinations


def generate_only_top_straight_combinations(roads_INSIDE_IN, roads_INSIDE_OUT, percentage):
    all_combinations = list(product(roads_INSIDE_IN, roads_INSIDE_OUT))
    
    # only consider combinations that are separated by at least and 1 intersections horizontally
    all_combinations[:] = [comb for comb in all_combinations
                           if (((int(comb[0].split("_")[3]) == 1) and (int(comb[1].split("_")[3]) == 1)) or ((int(comb[0].split("_")[3]) == 3) and (int(comb[1].split("_")[3]) == 3)))
                           and (int(comb[0].split("_")[1]) == int(comb[1].split("_")[1]))
                           and (int(comb[0].split("_")[2]) >= 9) and (int(comb[1].split("_")[2]) >= 9)
                           and (int(comb[0].split("_")[1]) >= 10) and (int(comb[1].split("_")[1]) >= 10)
                           and (np.abs(int(comb[0].split("_")[2]) - int(comb[1].split("_")[2])) >= 2)
                           and (comb[0] != comb[1])]
                            # and (int(comb[0].split("_")[2]) == 9) and (int(comb[1].split("_")[2]) == 11) 
        
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
        
        
    print(new)



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
    for combination in list(parameters["avenues_dic"].values()) + list(parameters["streets_dic"].values()):
        main_roads_IN.append(combination[0])
        main_roads_OUT.append(combination[1])
    
    
    # find all side inflowing and outflowing roads
    side_roads_IN = [road for road in parameters["side_roads"] if road in roads_IN]
    side_roads_OUT = parameters["side_roads"].difference(side_roads_IN)
    
    ### create combinations according to specifications
    # just creates lists out of the predefined dict
    avenues = generate_predefined_routes(parameters, "avenues_dic") # just creates lists out of the predefined dict
    streets = generate_predefined_routes(parameters, "streets_dic") # just creates lists out of the predefined dict
          
    # main to side roads
    #main_to_side = generate_valid_combinations(main_roads_IN, side_roads_OUT, road_adj_to_IN, parameters["mts"]["ratio"])
#
    ## side to side roads
    #side_to_side = generate_valid_combinations(side_roads_IN, side_roads_OUT, road_adj_to_IN, parameters["sts"]["ratio"])
    #
    ## side to main roads
    #side_to_main = generate_valid_combinations(side_roads_IN, main_roads_OUT, road_adj_to_IN, parameters["stm"]["ratio"])
    #                          
    ## inside to outside roads
    #inside_to_outside = generate_valid_combinations(roads_INSIDE, set(main_roads_OUT).union(side_roads_OUT), road_adj_to_IN, parameters["ito"]["ratio"], True)
    #                          
    ## outside to inside roads
    #outside_to_inside = generate_valid_combinations(set(main_roads_IN).union(side_roads_IN), roads_INSIDE, road_adj_to_IN, parameters["oti"]["ratio"], True)
    #
    ## inside to inside roads
    #inside_to_inside = generate_inside_combinations(roads_INSIDE, parameters["iti"]["ratio"])
    #
    ## horizontal traffic
    #horizontal_traffic = generate_horizontal_combinations(roads_INSIDE, parameters["horizontal"]["ratio"])
    #
    ## top traffic
    #top_traffic = generate_top_combinations(roads_INSIDE.union(side_roads_IN), roads_INSIDE.union(side_roads_OUT), parameters["top"]["ratio"])
    #
    ## left traffic
    #left_traffic = generate_left_combinations(roads_INSIDE.union(side_roads_IN), roads_INSIDE.union(side_roads_OUT), parameters["left"]["ratio"])
    #
    ## bottom traffic
    #bottom_traffic = generate_bottom_combinations(roads_INSIDE.union(side_roads_IN), roads_INSIDE.union(side_roads_OUT), parameters["bottom"]["ratio"])
    #
    #only_bottom = generate_only_bottom_straight_combinations(roads_INSIDE.union(side_roads_IN), roads_INSIDE.union(side_roads_OUT), parameters["only_bottom"]["ratio"])
    #                          
    #only_top = generate_only_top_straight_combinations(roads_INSIDE.union(side_roads_IN), roads_INSIDE.union(side_roads_OUT), parameters["only_top"]["ratio"])
    
    all_combinations = {
        "avenues": avenues,
        "streets": streets,
        #"mts": main_to_side,
        #"sts": side_to_side,
        #"stm": side_to_main,
        #"ito": inside_to_outside,
        #"oti": outside_to_inside,
        #"iti": inside_to_inside,
        #"horizontal": horizontal_traffic,
        #"top": top_traffic,
        #"left": left_traffic,
        #"bottom": bottom_traffic,
        #"only_bottom": only_bottom,
        #"only_top": only_top
    }
    
    check_flow(all_combinations)
    
    
    print("Number of routes generated (does not give all information about number of cars generated (different intervals))")
    print(f"avenues: {len(avenues)}")
    print(f"streets: {len(streets)}")
    #print(f"mts: {len(main_to_side)}")
    #print(f"sts: {len(side_to_side)}")
    #print(f"stm: {len(side_to_main)}")
    #print(f"ito: {len(inside_to_outside)}")
    #print(f"oti: {len(outside_to_inside)}")
    #print(f"iti: {len(inside_to_inside)}")
    #print(f"horizontal: {len(horizontal_traffic)}")
    #print(f"top: {len(top_traffic)}")
    #print(f"left: {len(left_traffic)}")
    #print(f"bottom: {len(bottom_traffic)}")
    #print(f"only bottom: {len(only_bottom)}")
    #print(f"only top: {len(only_top)}")
    print(f"Total flows: {sum(len(flow_list) for flow_list in all_combinations.values())}")
    
    return all_combinations