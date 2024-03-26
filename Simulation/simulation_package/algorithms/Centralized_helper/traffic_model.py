import gurobipy as gp
from gurobipy import GRB
from collections import defaultdict

from .model_inflow import traffic_inflow
from .model_outflow import traffic_outflow


def traffic_model_prediction(sim, model, opt_vars, lane_vehicle_count):
    """ Predicts future traffic situations based on the store-and-forward model"""
    
    for tau in range(sim.params["prediction_horizon"] + 1):
        
        # used in case there are multiple lanes with the same movement_id per intersection
        unique_movement_id = defaultdict(set)
        
        # used in traffic_outflow
        visited_downstream_roads = set()
        
        # current tl_update step (* scaling, since we defined prediction horizon differently than delta (see parameter_loader.py)
        tl_update = (tau * sim.params["scaling"]) // sim.params["delta"]
        
        
        for lane, lane_info in sim.lanes_data.items():
            
            #### do not need these conditions anymore
            # set initial conditions
            #if tau == 0:
            #    model.addConstr(opt_vars["q"][tau, lane] == lane_vehicle_count[lane], name = f"q_{tau}_{lane}")
            
            
            # Incoming traffic
            sum_inflow = traffic_inflow(sim, model, opt_vars, tau, lane, lane_info, tl_update, lane_vehicle_count)
                
                
            # Outflowing traffic 
            sum_outflow = traffic_outflow(sim, model, opt_vars, tau, lane, lane_info, visited_downstream_roads, tl_update, lane_vehicle_count)
            
            
            # Combine Inflow and Outflow 
            if tau == 0:
                
                model.addConstr((
                    opt_vars["q"][tau + 1, lane] == lane_vehicle_count[lane] + sum_inflow - sum_outflow
                    ),
                    name = f"q_{tau+1}_{lane}"
                )

            elif tau != sim.params["prediction_horizon"]:
                
                model.addConstr((
                    opt_vars["q"][tau + 1, lane] == opt_vars["q"][tau, lane] + sum_inflow - sum_outflow
                    ),
                    name = f"q_{tau+1}_{lane}"
                )
            
                
                    
            ################################################
            ########## Calculate Pressure per lane #########
            ################################################
            
            intersection_id = lane_info[0]
            movement_id = lane_info[1]
            
            # if it has a movement_id, then it is not an outflowing link of an intersection
            if isinstance(movement_id, int) and (movement_id not in unique_movement_id[intersection_id]):
                
                # add the movement_id to not include it twice
                unique_movement_id[intersection_id].add(movement_id)
                
                # determine which intersection the lane flows in
                intersection_id = lane_info[0]
                
                # check if movement_id appears twice in intersection
                same_movement_id_lane = [lane for lane in sim.intersections_data[intersection_id]["inflow"] if sim.lanes_data[lane][1] == movement_id]
                
                
                inter_id = lane_info[0]
                downstream_lanes = lane_info[3]
                
                if tau == 0:
                    
                    total_vehicle_count = sum(lane_vehicle_count[lane] for lane in same_movement_id_lane)
                    
                    model.addConstr((
                        opt_vars["p_m"][tau, inter_id, movement_id] == total_vehicle_count - sum(lane_vehicle_count[d_lane] for d_lane in downstream_lanes) / len(downstream_lanes)
                        ),
                        name = f"p_m_{tau}_{inter_id}_{movement_id}"
                    )
                    
                else:
                    
                    total_vehicle_count = gp.quicksum(opt_vars["q"][tau, lane] for lane in same_movement_id_lane)
                    
                    model.addConstr((
                        opt_vars["p_m"][tau, inter_id, movement_id] == total_vehicle_count - gp.quicksum(opt_vars["q"][tau, d_lane] for d_lane in downstream_lanes) / len(downstream_lanes)
                        ),
                        name = f"p_m_{tau}_{inter_id}_{movement_id}"
                    )