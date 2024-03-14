def activate_tl(sim, new_phases):
    """ Activates new phases for each intersection
    
    Parameters
    -----------
    sim : Simulation
        Object of the Simulation Class
    
    new_phases : dict
        The keys are intersection id's and the value is the new chosen phase
    """
    
    for intersection in sim.intersections_data:
        
        sim.engine.set_tl_phase(intersection, new_phases[intersection])
        sim.perform["current_phase"][intersection] = new_phases[intersection]
        
        
def idle_time_activate_tl(sim):
    """ Activates idle time phases for each intersection (i.e. all red)
    The all red phase is set in the roadnet file as the len(phases)'th phase
    
    Parameters
    -----------
    sim : Simulation
        Object of the Simulation Class
    
    new_phases : dict
        The keys are intersection id's and the value is the new chosen phase
    """
    
    for intersection in sim.intersections_data:
        
        phase_type = sim.params["intersection_phase"][intersection]
        sim.engine.set_tl_phase(intersection, len(sim.params["all_phases"][phase_type]))
    