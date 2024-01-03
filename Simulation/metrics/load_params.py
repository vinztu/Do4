def load_specific_params(sim):
    
    # used for the directory name
    important_info = [sim.params["delta"], sim.params["idle_time"], sim.params["sim_duration"]]
    
    
    if sim.algorithm == "MP":
        specific_params = {}
    
    if sim.algorithm == "CA_MP":
        specific_params = {
            "c_inf": sim.params["c_inf"],
            "m": sim.params["m"]
        }
        important_info = important_info + list(specific_params.values())
        
    if sim.algorithm == "Centralized":
        specific_params = {
            "prediction_horizon": sim.params["prediction_horizon"],
            "num_tl_updates": sim.params["num_tl_updates"],
            "scaling": sim.params["scaling"],
            "exogenous_inflow": sim.params["exogenous_inflow"],
            "alpha": sim.params["alpha"]
        }
        important_info = important_info + list(specific_params.values())
    
    if "LDPP-T" in sim.algorithm:
        specific_params = {
            "max_it": sim.params["max_it"],
            "rho": sim.params["rho"],
            "z_domain": sim.params["z_domain"],
            "L": sim.params["L"],
            "V1": sim.params["V1"],
            "V2": sim.params["V2"],
            "V3": sim.params["V3"]
        }
        important_info = important_info + list(specific_params.values())
    
    if "LDPP-GF" in sim.algorithm:
        specific_params = {
            "max_it": sim.params["max_it"],
            "rho": sim.params["rho"],
            "z_domain": sim.params["z_domain"],
            "lane_weight": sim.params["lane_weight"],
            "V": sim.params["V"]
        }
        important_info = important_info + list(specific_params.values())
        
    
    return important_info, specific_params