import numpy as np
import random
import json
import os
from collections import Counter, defaultdict
from generate_routes import generate_random_routes, generate_specific_routes


def divide_remaining_cars_on_routes(total_routes, total_cars):
    """ divide the module "number" of cars onto the last remaining routes per category"""

    rest = ((total_cars/total_routes) - (total_cars//total_routes)) * total_routes

    best_divisor = 1
    min_remainder = float('inf')  # Initialize with positive infinity

    for div in range(min(10,total_routes) , 0, -1):
        remainder = rest % div
        if remainder < min_remainder:
            increase_num_car_per_route = int(round(rest / div))
            best_divisor = div
            if remainder < 0.1:
                break
                
    return best_divisor, increase_num_car_per_route


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
    sum_routes = 0
    sum_vehicles = 0
    flow = []
    
    print("Number of routes and number of cars in category generated")
    for category, routes in routes_dict.items():
    
        if "_" in category:
            # number of different routes
            number_of_routes_in_category = len(routes)
            
            # total number of cars in category
            total_cars_in_category = parameters["proportions"][category][0] * parameters["total_demand"]
            
            # number of cars per route (give minimal 1 car)
            cars_per_route = max(2,  total_cars_in_category // number_of_routes_in_category)
            
            # handle to module part to spread the remaining cars
            best_divisor, increase_num_car_per_route = divide_remaining_cars_on_routes(number_of_routes_in_category, total_cars_in_category)
            choose_which_routes = np.random.choice(number_of_routes_in_category, size=best_divisor, replace=False)
            
            if parameters["proportions"][category][0] * parameters["total_demand"] / number_of_routes_in_category <= 2:
                print(f'WARNING: Less than 2 cars generated per lane in category {category}. Currently: {round(parameters["proportions"][category][0] * parameters["total_demand"] / number_of_routes_in_category,4)}.\n Decrease Percentage # possible routes in proportions dict for this category to increase generated cars per route. Necessary to reach specified total demand')
            
        for index, route in enumerate(routes):
            
            # define start and end time
            # if cars_per_route is too small, then the interval will be really large.
            # --> This leads to cars being generated only at the beginning and once at the end
            if cars_per_route <= 9:
                startTime = random.randint(0, 1300)
                endTime = random.randint(2800, 3800)
                
            if cars_per_route <= 5:
                startTime = random.randint(0, 1600)
                endTime = random.randint(2500, 3800)
                
            else:
                startTime = random.randint(0, 400)
                endTime = random.randint(3800, 4000)
            
            
            if random_routes:
                interval = parameters["interval"]
            
            # check if its a main road
            elif "_" in category:
                
                # need to create cars_per_route cars during the entire duration
                if index in choose_which_routes:
                    # increase selected routes by 1
                    interval = float(round((endTime - startTime) / (cars_per_route + increase_num_car_per_route - 1), 2))
                else:
                    interval = float(round((endTime - startTime) / (cars_per_route - 1), 2))
                    
                
            else:
                # increase the interval if that road has many combinations
                # such that the effective interval between 2 cars remains the same
                interval = parameters[category]["effective_interval"] * count_starting_roads[route[0]]
                
                startTime = random.randint(0, 3000)
                endTime = min(4000, startTime + interval * 3)
                
            
            
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
            
        
        sum_routes += len(routes)
        sum_vehicles += len(num_vehicles[category])
        print(f"For {category}:{'':<7} # Routes = {len(routes):<7} # Cars = {len(num_vehicles[category])}")
        print()
    
    print(f"Total routes: {sum_routes}, Total cars: {sum_vehicles}")
    # write json file
    json.dump(flow, open(os.path.join(directory, FlowFile), "w"), indent=2)
    
    print()
    print("Successful created a flow file!")
    
    return routes_dict, num_vehicles