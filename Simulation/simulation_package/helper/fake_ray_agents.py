"""
Do some initial "computations" to warm up ray. Otherwise, first iteration takes "much" longer. (not consistent with computation time of the remaining iterations)
"""

import time
import ray

@ray.remote(num_cpus = 1, scheduling_strategy="SPREAD")
def fake_agent_agent():
    time.sleep(0.3)
    
    
def fake_agent(sim):
    e = []
    for i in range(sim.cpu):
        e.append(fake_agent_agent.remote())

    ray.get(e)