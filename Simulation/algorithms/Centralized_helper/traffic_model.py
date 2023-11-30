import gurobipy as gp
from gurobipy import GRB

from Simulation.algorithms.Centralized_helper.model_inflow import traffic_inflow
from Simulation.algorithms.Centralized_helper.model_outflow import traffic_outflow


def traffic_model_prediction(sim, model, opt_vars, lane_vehicle_count):
    """ Predicts future traffic situations based on the store-and-forward model"""
    
    for tau in range(sim.params["prediction_horizon"] + 1):
        
        # used in traffic_outflow
        visited_downstream_roads = set()
        
        # current tl_update step (* scaling, since we defined prediction horizon differently than delta (see parameter_loader.py)
        tl_update = (tau * sim.params["scaling"]) // sim.params["delta"]
        
        
        for lane, lane_info in sim.lanes_data.items():
            
            # set initial conditions
            if tau == 0:
                model.addConstr(opt_vars["q"][tau, lane] == lane_vehicle_count[lane], name = f"q_{tau}_{lane}")
            
            
            # Incoming traffic
            sum_inflow = traffic_inflow(sim, model, opt_vars, tau, lane, lane_info, tl_update)
                
                
            # Outflowing traffic 
            sum_outflow = traffic_outflow(sim, model, opt_vars, tau, lane, lane_info, visited_downstream_roads, tl_update)
            
            
            # Combine Inflow and Outflow 
            if tau != sim.params["prediction_horizon"]:
                
                model.addConstr((
                    opt_vars["q"][tau + 1, lane] == opt_vars["q"][tau, lane] + sum_inflow - sum_outflow
                    ),
                    name = f"q_{tau+1}_{lane}"
                )
                
                    
            ################################################
            ########## Calculate Pressure per lane #########
            ################################################
            
            movement_id = lane_info[1]
            
            # if it has a movement_id, then it is not an outflowing link of an intersection
            if isinstance(movement_id, int):
                
                ######################################################
                #!!!!!!!Assume that we only have 1 lane per movement
                # --> 3 lanes per road (not more)
                ######################################################
                
                inter_id = lane_info[0]
                downstream_lanes = lane_info[3]
                
                model.addConstr((
                    opt_vars["p_m"][tau, inter_id, movement_id] == opt_vars["q"][tau, lane] - gp.quicksum(opt_vars["q"][tau, d_lane] for d_lane in downstream_lanes) / len(downstream_lanes)
                    ),
                    name = f"p_m_{tau}_{inter_id}_{movement_id}"
                )