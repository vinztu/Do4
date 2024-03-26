import re

def label_name(algorithm, meta_info, params, save_fig_info):
    
    meta = meta_info[algorithm]
    
    algorithm_short = algorithm.split("_")[0]
    
    if algorithm.startswith("Fixed-Time"):
        if save_fig_info["final_plot"]:
            label = "FT" #algorithm_short
        else:
            label = algorithm_short + "_D_" + str(meta["delta"]) + "_IT_" + str(meta["idle_time"])
    
    elif algorithm.startswith("MP"):
        if save_fig_info["final_plot"]:
            label = "MP"
        else:
            label = algorithm_short + "_D_" + str(meta["delta"]) + "_IT_" + str(meta["idle_time"])
        
    elif algorithm.startswith("CA_MP"):
        if save_fig_info["final_plot"]:
            label = "CA BP"
        else:
            label = algorithm_short + "_D_" + str(meta["delta"]) + "_IT_" + str(meta["idle_time"]) + "_Cinf_" + str(meta["c_inf"]) + "_m_" + str(meta["m"])
        
    elif algorithm.startswith("Centralized"):
        if save_fig_info["final_plot"]:
            label = "Centralized"
        else:
            label = algorithm_short + "_D_" + str(meta["delta"]) + "_IT_" + str(meta["idle_time"]) + "_PH_" + str(meta["prediction_horizon"]) \
                    + "_K_" + str(meta["scaling"]) + "_EI_" + str(meta["exogenous_inflow"]) + "_AL_" + str(meta["alpha"])
        
    elif algorithm.startswith("LDPP-T"):
        if save_fig_info["final_plot"]:
            consensus = re.split('[-_]', algorithm)[2]
            label = f"LDPP ({consensus})"
        else:
            label = algorithm_short + "_D_" + str(meta["delta"]) + "_IT_" + str(meta["idle_time"]) + "_RHO_" + str(meta["rho"]) \
                    + "_z_" + meta["z_domain"] + "_L_" + str(meta["L"]) + "_V1_" + str(meta["V1"]) + "_V2_" + str(meta["V2"]) \
                    + "_V3_" + str(meta["V3"])
        
    elif algorithm.startswith("LDPP-GF"):
        if save_fig_info["final_plot"]:
            consensus = re.split('[-_]', algorithm)[2]
            label = f"LDPP ({consensus})"
        else:
            label = algorithm_short + "_D_" + str(meta["delta"]) + "_IT_" + str(meta["idle_time"]) + "_RHO_" + str(meta["rho"]) \
                    + "_z_" + meta["z_domain"] + "_lw_" + meta["lane_weight"] + "_V_" + str(meta["V"])

        
    return label