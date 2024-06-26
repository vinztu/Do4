import numpy as np

def compute_normalized_pressure(arguments, intersection):
    """
    First, compute the normalized pressure for each movement (weight)
    Then compute the pressure for each phase
    
    2 differences:
     - normalization
     - use entire road (not just lane) to compute pressure per lane 

    Parameters
    ----------
    sim : Simulation
        A simulation class object
        
    Returns
    -------
    pressure_per_movement : dict
        A dictionary with all pressures from each phase
        The keys are movement_id and the correponding pressures (per movement) as values

    pressure_per_movement: list
        A list with all pressures per phase
    """
    
    ##############################################################################
    # Calculate pressure per movement
    ##############################################################################
    
    
    max_movement_id = max([arguments["lanes_data"][lane][1] for lane in arguments["intersections_data"][intersection]["inflow"]])
    
    pressure_per_movement = {}
    
    inflow_lanes = arguments["intersections_data"][intersection]["inflow"]
    
    for movement_id in range(max_movement_id + 1):
        
        lanes_with_movement_id = [lane for lane in inflow_lanes if arguments["lanes_data"][lane][1] == movement_id]
        
        # take any downstream lane (only road matters and not specific lane)
        d_lane = arguments["lanes_data"][lanes_with_movement_id[0]][3][0]
        
        # d_ab is defined as by Gregoire et al.
        num_vehicles = np.array([arguments["lane_vehicle_count"][lane] for lane in lanes_with_movement_id])
        d_ab = 1 if np.any(num_vehicles != 0) else 0
        
        # !!! Different pressure definition max(0, MP_pressure) (contrary to the definition, the saturation flow rate gets multiplied already here)
        pressure_per_movement[movement_id] = d_ab * max(0, normalize_lane(lanes_with_movement_id[0], arguments) - normalize_lane(d_lane, arguments)) * arguments["params"]["saturation_flow"]
        

    
    ##############################################################################
    # Calculate pressure per phase
    ##############################################################################
    pressure_per_phase = []
    
    phase_type = arguments["params"]["intersection_phase"][intersection]

    for phase in arguments["params"]["all_phases"][phase_type].values():

        pressure = sum( list( map(pressure_per_movement.get, phase)))

        pressure_per_phase.append(pressure)
            
            
    return pressure_per_movement, pressure_per_phase



def normalize_lane(lane, arguments):
    """ Definition according to Jean Gregoire et al."""

    filtered_lanes = [l for l in arguments["lanes_data"] if l[:-2] in lane]
    
    # !!! Difference to MP: Consider all vehicles on a ROAD (not lane) to calculate the pressure
    num_vehicles = sum(arguments["lane_vehicle_count"][l] for l in filtered_lanes)
    
    # Total Capacity of all lanes
    total_capacity = sum(arguments["params"]["capacity"][l] for l in filtered_lanes)
    
    nominator = (num_vehicles/arguments["params"]["c_inf"]) + ((2 - (total_capacity/arguments["params"]["c_inf"])) * ((num_vehicles/total_capacity) ** arguments["params"]["m"]))
    
    denominator = 1 + ((num_vehicles/total_capacity) ** (arguments["params"]["m"]-1))
    
    return min(1, nominator/denominator)