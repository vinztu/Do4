from collections import defaultdict

def compute_pressure(sim):
    """
    First, compute the pressure for each movement (weight)
    Then compute the pressure for each phase

    Parameters
    ----------
    sim : Simulation
        A simulation class object
        
    Returns
    -------
    pressure_per_movement : dict{dict}
        A dictionary with all pressures from each phase
        The outer keys are all intersections id
        The inner keys are movement_id and the correponding pressures (per movement) as values

    pressure_per_movement: dict{list}
        A dictionary with intersection id as keys and the inner list consists of the 
        pressure per phase
    """
    
    
    pressure_per_movement = defaultdict(dict)
    
    # get number of vehicles on each lane
    lane_vehicle_count = sim.engine.get_lane_vehicle_count()
    
    ##############################################################################
    # Calculate pressure per movement
    ##############################################################################
    
    for lane, [inter_id, movement_id, upstream_lanes, downstream_lanes] in sim.lanes_data.items():
        
        # this condition ensures that if we have multiple lanes with the same movement_id (same direction)
        # then we only count the downstream lanes 1 times instead of multiple times
        if isinstance(movement_id, int):
            if movement_id not in pressure_per_movement[inter_id]:
                # here we assume a uniform turn ratio
                pressure_per_movement[inter_id][movement_id] = lane_vehicle_count[lane] - \
                                                            sum(lane_vehicle_count[l] for l in downstream_lanes)/len(downstream_lanes)
            else:
                pressure_per_movement[inter_id][movement_id] += lane_vehicle_count[lane]

                    
    ##############################################################################
    # Calculate pressure per phase
    ##############################################################################
    pressure_per_phase = defaultdict(list)

    for intersection in sim.intersections_data:
        for index, phase in enumerate(sim.params["phases"].values()):

            pressure = sum( list( map(pressure_per_movement[intersection].get, phase)))
            
            pressure_per_phase[intersection].append(pressure)
            
            
    return dict(pressure_per_movement), dict(pressure_per_phase) 