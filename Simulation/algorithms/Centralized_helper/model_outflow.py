import gurobipy as gp
from gurobipy import GRB

def traffic_outflow(sim, model, opt_vars, tau, lane, lane_info, visited_downstream_roads, tl_update):
    """ Computes the outflow of cars into the lane at time tau"""
    
    inter_id = lane_info[0]
    movement_id = lane_info[1]
    downstream_lanes = lane_info[3]
    
    if downstream_lanes:
    
        # all lanes are on the same road (take 0'th index as an example)
        downstream_road = downstream_lanes[0][:-2]

        # only set this constraint once for all downstream_lanes
        # since it considers roads and not lanes
        if downstream_road not in visited_downstream_roads:

            # add it to the set
            visited_downstream_roads.add(downstream_road)

            # determine the lane with the maximal number of cars
            model.addConstr((
                opt_vars["max_lane"][tau, downstream_road] == gp.max_([opt_vars["q"][tau, d_lane] for d_lane in downstream_lanes])
                ),
                name = f"max_lane_{tau}_{downstream_road}"
            )

            # determine the max free capacity for the downstream road
            # assume all lanes in a road have the same capacity
            model.addConstr((
                opt_vars["free_capacity"][tau, downstream_road] == sim.params["capacity"][downstream_lanes[0]] - opt_vars["max_lane"][tau, downstream_road]
                ),
                name = f"free_capacity_{tau}_{downstream_road}"
            )


        # determine the actual outflow out of a lane
        model.addConstr((
            opt_vars["outflow"][tau, lane] == gp.min_(opt_vars["q"][tau, lane], sim.params["saturation_flow"], opt_vars["free_capacity"])
            ),
            name = f"outflow_{tau}_{lane}"
        )

        # return all possible phases that the current lane is part of
        possible_phases_per_lane = [phase for phase, phase_movements in sim.params["phases"].items() if movement_id in phase_movements]

        sum_outflow = opt_vars["outflow"][tau, lane] * gp.quicksum(opt_vars["phi"][tl_update, inter_id, phi] for phi in possible_phases_per_lane)

    # if there are no downstream lanes, we assume that cars "disappear" with the saturation flow rate
    else:

        model.addConstr((
            opt_vars["outflow"][tau, lane] == gp.min_(opt_vars["q"][tau, lane], sim.params["saturation_flow"])
            ),
            name = f"outflow_{tau}_{lane}"
        )

        sum_outflow = opt_vars["outflow"][tau, lane]
    
    return sum_outflow