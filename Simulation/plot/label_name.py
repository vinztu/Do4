def label_name(algorithm, meta_info, params):
    
    meta = meta_info[algorithm]
    
    algorithm_short = algorithm.split("_")[0]

    if algorithm.startswith("MP"):
        label = algorithm_short + "_D_" + str(meta["delta"]) + "_IT_" + str(meta["idle_time"])
        
    elif algorithm.startswith("CA_MP"):
        label = algorithm_short + "_D_" + str(meta["delta"]) + "_IT_" + str(meta["idle_time"]) + "_Cinf_" + str(meta["c_inf"]) + "_m_" + str(meta["m"])
        
    elif algorithm.startswith("Centralized"):
        label = algorithm_short + "_D_" + str(meta["delta"]) + "_IT_" + str(meta["idle_time"]) + "_PH_" + str(meta["prediction_horizon"]) \
                + "_K_" + str(meta["scaling"]) + "_EI_" + str(meta["exogenous_inflow"]) + "_AL_" + str(meta["alpha"])
        
    elif algorithm.startswith("LDPP-T"):
        label = algorithm_short + "_D_" + str(meta["delta"]) + "_IT_" + str(meta["idle_time"]) + "_RHO_" + str(meta["rho"]) \
                + "_z_" + meta["z_domain"] + "_L_" + str(meta["L"]) + "_V1_" + str(meta["V1"]) + "_V2_" + str(meta["V2"]) \
                + "_V3_" + str(meta["V3"])
        
    elif algorithm.startswith("LDPP-GF"):
        label = algorithm_short + "_D_" + str(meta["delta"]) + "_IT_" + str(meta["idle_time"]) + "_RHO_" + str(meta["rho"]) \
                + "_z_" + meta["z_domain"] + "_lw_" + meta["lane_weight"] + "_V_" + str(meta["V"])
        
    return label