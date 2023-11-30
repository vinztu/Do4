def compute_pressure(arguments, intersection):
    """
    First, compute the normalized pressure for each movement (weight)
    Then compute the pressure for each phase

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
    
    # get number of vehicles on each lane
    lane_vehicle_count = arguments["lane_vehicle_count"]
    
    for lane in arguments["intersections_data"][intersection]["inflow"]:
        
        movement_id = arguments["lanes_data"][lane][1]
        
        if movement_id not in pressure_per_movement:
            downstream_lanes = arguments["lanes_data"][lane][3]
            # here we assume a uniform turn ratio
            pressure_per_movement[movement_id] = (lane_vehicle_count[lane] - sum(lane_vehicle_count[l] for l in downstream_lanes)/len(downstream_lanes)) * arguments["params"]["saturation_flow"]
        else:
            pressure_per_movement[movement_id] += lane_vehicle_count[lane] * arguments["params"]["saturation_flow"]

                    
    ##############################################################################
    # Calculate pressure per phase
    ##############################################################################
    pressure_per_phase = []

    for index, phase in enumerate(arguments["params"]["phases"].values()):

        pressure = sum( list( map(pressure_per_movement.get, phase)))

        pressure_per_phase.append(pressure)
            
            
    return pressure_per_movement, pressure_per_phase
