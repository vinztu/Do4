from Simulation.algorithms.Centralized_helper.model import create_model
from Simulation.algorithms.Centralized_helper.traffic_model import traffic_model_prediction
from Simulation.algorithms.Centralized_helper.pressure_phase import compute_pressure_per_phase
from Simulation.algorithms.Centralized_helper.phase import set_phase_constraints
from Simulation.algorithms.Centralized_helper.objective import set_objective
from Simulation.algorithms.Centralized_helper.optimizer import optimizer


def Centralized_MP(sim):
    """
    Compute 1 iteraction of the centralized formulation (without any additional modifications)
    """
    
    # create the model and all optimization variables
    model, opt_vars = create_model(sim)
                                
    # retrieve lane information from cityflow
    lane_vehicle_count = sim.engine.get_lane_vehicle_count()
    
    # set up all constraints based on the store-and-forward model
    # and define pressure per movement
    traffic_model_prediction(sim, model, opt_vars, lane_vehicle_count)
    
    # define pressure per movement
    compute_pressure_per_phase(sim, model, opt_vars)
    
    # set phase constraints (only 1 phase can be active at a time)
    set_phase_constraints(sim, model, opt_vars)
    
    # define the objective
    set_objective(sim, model, opt_vars)
    
    #model.write("new.lp")
    
    # optimize the model
    optimal_phases = optimizer(sim, model, opt_vars)
    
    model.dispose()
    
    return optimal_phases