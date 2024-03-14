from .tl_activation import idle_time_activate_tl

# proceed the simulation for Delta timesteps 
def sim_step(sim, metrics_recorder, current_time):

    # simulate for delta - idle time seconds
    for tau in range(sim.params["delta"] - sim.params["idle_time"]):
        sim.engine.next_step()
        
        # update performance measure for every time step
        metrics_recorder.frequent_update(sim, current_time + tau)


    # update current time
    current_time += sim.params["delta"] - sim.params["idle_time"]
    
    if sim.params["idle_time"] != 0:
        # apply idle time where all tl are red
        idle_time_activate_tl(sim)

        # simulate the idle time
        for tau in range(sim.params["idle_time"]):
            # advance the simulation by (Delta - idle_time) time steps
            sim.engine.next_step()

            # update performance measure for every time step
            metrics_recorder.frequent_update(sim, current_time + tau)
        