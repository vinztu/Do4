import numpy as np
import random
import json
import os
from collections import Counter, defaultdict
from generator.generate_routes import generate_random_routes, generate_specific_routes

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
                         roads_IN: list = None,
                         roads_OUT: list = None,
                         road_adj_to_IN: dict = {},
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
        routes_dict = generate_random_routes(roads_IN, roads_OUT, road_adj_to_IN, parameters)
    else:
        routes_dict = generate_specific_routes(roads_IN, roads_OUT, road_adj_to_IN, parameters)
        all_first_roads = [road[0] for sublist in routes_dict.values() for road in sublist]
        # convert it to a defaultdict, so in case the key does not exist, it will display a (0,0)
        count_starting_roads = defaultdict(int, Counter(all_first_roads))
    
    
    
    flow = []
    for desc, routes in routes_dict.items():
        
        for route in routes:

            # regulate amount of inflowing cars
            # if no endTime --> endTime = -1
            startTime = np.random.randint(0,40)
            endTime = -1


            if random_routes:
                interval = parameters["interval"]
            else:
                # increase the interval if that road has many combinations
                # such that the effective interval between 2 cars remains the same
                interval = parameters[desc]["effective_interval"] * count_starting_roads[route[0]]


                
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
        
    # write json file
    json.dump(flow, open(os.path.join(directory, FlowFile), "w"), indent=2)
    print("Successful created a flow file!")