import numpy as np
import random
import json
import os
from collections import Counter, defaultdict
from generate_routes import generate_random_routes, generate_specific_routes

def write_json_flow_file(vehLen: int = 5,
                         vehWidth: int = 2,
                         vehMaxPosAcc: float = 2.0,
                         vehMaxNegAcc: float = 4.5,
                         vehUsualPosAcc: float = 2.0,
                         vehUsualNegAcc: float = 4.5,
                         vehMinGap: float = 2.5,
                         vehMaxSpeed: float = 16.67,
                         vehHeadwayTime: float = 1.5,
                         parameters: dict = {},
                         roads_IN: set = set(),
                         roads_OUT: set = set(),
                         road_adj_to_IN: dict = {},
                         roads_INSIDE: set = set(),
                         directory: str = "./",
                         FlowFile: str = "flow",
                         random_routes: bool = False,
                         random_vehicle_parameters: bool = True
                        ):
    """write the flow file in json format

    Args:
        vehLen (int): Vehicel length. Defaults to 5.
        vehWidth (int): Vehicel Width. Defaults to 2.
        vehMaxPosAcc (float): maximum acceleration (in m/s). Defaults to 2.0.
        vehMaxNegAcc (float): maximum deceleration. Defaults to 4.5.
        vehUsualPosAcc (float):  usual acceleration. Defaults to 2.0.
        vehUsualNegAcc (float): usual deceleration. Defaults to 4.5.
        vehMinGap (float): minimum acceptable gap with leading vehicle. Defaults to 2.5.
        vehMaxSpeed (float): maximum cruising speed. Defaults to 16.67.
        vehHeadwayTime (float): desired headway time (in seconds) with leading vehicle, keep current speed . Defaults to 1.5.
        roads_IN (list) : list of all roads that enter the whole network (start point is a virtual intersection) Defaults to None
        roads_OUT (list) : list of all roads that leave the whole network (end point is a virtual intersection) defaults to None
        road_adj_to_IN (dict) : keys are roads that enter the network and values are the corresponding roads that leave the network in the same direction as the inflowing road (avoid these situations) Defaults to {}
        parameters (dict) : routes parameters set in main(). Defaults to {}
        directory (str): directory where to save the flow file. Defaults to "./".
        FlowFile (str): name of the flowFile. Defaults to "flow".
        random_routes (bool): randomize routes or not
        random_vehicle_parameters (bool): randomize vehicle parameters or not
    """
    
    if random_routes:
        # generate all combinations with those roads
        routes_dict = generate_random_routes(roads_IN, roads_OUT, roads_INSIDE, road_adj_to_IN, parameters)
    else:
        routes_dict = generate_specific_routes(roads_IN, roads_OUT, road_adj_to_IN, roads_INSIDE, parameters)
        all_first_roads = [road[0] for sublist in routes_dict.values() for road in sublist]
        # convert it to a defaultdict, so in case the key does not exist, it will display a (0,0)
        count_starting_roads = defaultdict(int, Counter(all_first_roads))
    
    num_vehicles = defaultdict(list)
    flow = []
    for category, routes in routes_dict.items():
        
        if "_" in category:
            # number of different routes
            number_of_routes_in_category = len(routes)
            
            # number of cars per route (give minimal 1 car)
            cars_per_route = max(1, parameters["proportions"][category][0] * parameters["total_demand"] / number_of_routes_in_category)
                
            if cars_per_route == 1:
                print(f'WARNING: Less than 1 car generated per lane in category {category}. Currently: {parameters["proportions"][category][0] * parameters["total_demand"] / number_of_routes_in_category}. Decrease Percentage # possible routes in proportions dict for this category.')
            
            print(f'category: {category}, num cars: {parameters["proportions"][category][0] * parameters["total_demand"]}')
        
        pr = False
        
        for route in routes:
            
            # define start and end time
            # if cars_per_route is too small, then the interval will be really large.
            # --> This leads to cars being generated only at the beginning and once at the end
            if cars_per_route <= 7 and cars_per_route > 5:
                startTime = random.randint(0, 1000)
                endTime = random.randint(3000, 4000)
            
            elif cars_per_route <= 5:
                startTime = random.randint(0, 1900)
                endTime = random.randint(2200, 4000)
                
            else:
                startTime = random.randint(0, 400)
                endTime = random.randint(3800, 4000)
            
            if random_routes:
                interval = parameters["interval"]
            
            # check if its a main road
            elif "_" in category:
                # need to create cars_per_route cars during the entire duration
                interval = float(round((endTime - startTime) / cars_per_route, 2))
                if not pr:
                    print(f"interval, category: {category}, interval: {interval}, cars per route: {cars_per_route}")
                    print()
                    pr = True
                
            else:
                # increase the interval if that road has many combinations
                # such that the effective interval between 2 cars remains the same
                interval = parameters[category]["effective_interval"] * count_starting_roads[route[0]]
                
                
            
            if random_vehicle_parameters:
                # slighly randomize further parameters
                vehMaxPosAcc = random.uniform(2.5, 4.0)
                vehMaxNegAcc = random.uniform(3, 5)
                vehUsualPosAcc = random.uniform(1.9, 2.5)
                vehUsualNegAcc = random.uniform(2, 3)
                vehMinGap = random.uniform(2, 3)
                vehMaxSpeed = random.uniform(15, 18)
                vehHeadwayTime = random.uniform(2, 7)

            # combine all vehicle infos
            vehicle_template = {
                "length": vehLen,
                "width": vehWidth,
                "maxPosAcc": vehMaxPosAcc,
                "maxNegAcc": vehMaxNegAcc,
                "usualPosAcc": vehUsualPosAcc,
                "usualNegAcc": vehUsualNegAcc,
                "minGap": vehMinGap,
                "maxSpeed": vehMaxSpeed,
                "headwayTime": vehHeadwayTime
            }

            # append the new vehicle flow to the list
            flow.append({
                "vehicle": vehicle_template,
                "route": route,
                "interval": interval, # defines the interval of consecutive vehicles (in seconds)
                "startTime": startTime,
                "endTime": endTime
            })
            
            
            ### count the number of generated vehicles
            num_interval = (endTime - startTime + 1) // interval

            mod_interval = (endTime - startTime + 1) % interval != 0

            number_of_generated_cars = int(num_interval + mod_interval)   

            for car_start in range(number_of_generated_cars):
                num_vehicles[category].append(int(startTime + interval * car_start))


    # write json file
    json.dump(flow, open(os.path.join(directory, FlowFile), "w"), indent=2)
    print("Successful created a flow file!")
    
    return routes_dict, num_vehicles