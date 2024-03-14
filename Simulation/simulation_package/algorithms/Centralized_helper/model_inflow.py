import gurobipy as gp
from gurobipy import GRB

def traffic_inflow(sim, model, opt_vars, tau, lane, lane_info, tl_update, lane_vehicle_count):
    """ Computes the inflow of cars into the lane at time tau"""
    
    sum_inflow = 0
    
    # all upstream lanes
    upstream_lanes = lane_info[2]
            
    # minimum between q and saturation flow
    # determines the maximal possible number of cars the can move in one time step
    if tau == 0:
        model.addConstr((
            opt_vars["min_flow"][tau, lane] == gp.min_(lane_vehicle_count[lane], sim.params["saturation_flow"])
            ),
            name = f"min_flow_{tau}_{lane}"
        )
    else:
        model.addConstr((
            opt_vars["min_flow"][tau, lane] == gp.min_(opt_vars["q"][tau, lane], sim.params["saturation_flow"])
            ),
            name = f"min_flow_{tau}_{lane}"
        )

        
    # if there are upstream lanes, calculate the inflow, else set it to a constant flow
    if upstream_lanes:

        # cars arriving on a road will be "split" among neighbouring lanes
        neighboring_lanes = [l for l in sim.lanes_data if l[:-2] in lane]

        for u_lane in upstream_lanes:

            # movement_id & inter_id for u_lane
            u_lane_int_id = sim.lanes_data[u_lane][0]
            u_lane_movement = sim.lanes_data[u_lane][1] # movement_id
            
            # find out which phases includes that movement_id
            u_intersection_phase_type = sim.params["intersection_phase"][u_lane_int_id]

            # return all possible phases that the current lane is part of
            possible_phases_per_u_lane = [phase for phase, phase_movements in sim.params["all_phases"][u_intersection_phase_type].items() if u_lane_movement in phase_movements]

            # depending on the default phases definition (right turns)
            if not possible_phases_per_u_lane:
                possible_phases_per_u_lane = list(range(len(sim.params["all_phases"][u_intersection_phase_type])))

            sum_inflow += (1/len(neighboring_lanes)) * opt_vars["min_flow"][tau, u_lane] * gp.quicksum([opt_vars["phi"][tl_update, u_lane_int_id, phi] for phi in possible_phases_per_u_lane])

    else:       
        sum_inflow = sim.params["exogenous_inflow"]
        
        
    return sum_inflow