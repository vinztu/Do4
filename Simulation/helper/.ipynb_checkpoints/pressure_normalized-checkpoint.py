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
    
    pressure_per_movement = {}
    
    for lane in arguments["intersections_data"][intersection]["inflow"]:

        movement_id = arguments["lanes_data"][lane][1]

        # here we assume a uniform turn ratio
        # !!! Different pressure definition max(0, MP_pressure)
        pressure_per_movement[movement_id] = arguments["params"]["saturation_flow"] * max(0, normalize_lane(lane, arguments) - normalize_lane(lane, arguments))

                    
    ##############################################################################
    # Calculate pressure per phase
    ##############################################################################
    pressure_per_phase = []

    for index, phase in enumerate(arguments["params"]["phases"].values()):

        pressure = sum( list( map(pressure_per_movement.get, phase)))

        pressure_per_phase.append(pressure)
            
            
    return pressure_per_movement, pressure_per_phase



def normalize_lane(lane, arguments):
    """ Definition according to Jean Gregoire et al."""

    # !!! Difference to MP: Consider all vehicles on a ROAD (not lane) to calculate the pressure
    num_vehicles = sum(arguments["lane_vehicle_count"][l] for l in arguments["lanes_data"] if l[:-2] in lane)
    
    nominator = (num_vehicles/arguments["params"]["c_inf"]) + (2 - (arguments["params"]["capacity"][lane]/arguments["params"]["c_inf"])) * ((num_vehicles/arguments["params"]["capacity"][lane]) ** arguments["params"]["m"])
    
    denominator = 1 + ((num_vehicles/arguments["params"]["capacity"][lane]) ** (arguments["params"]["m"]-1))
    
    return min(1, nominator/denominator)