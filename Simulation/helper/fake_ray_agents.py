"""
Do some initial "computations" to warm up ray. Otherwise, first iteration takes "much" longer. (not consistent with computation time of the remaining iterations)
"""

import time
import ray

@ray.remote
def fake_agent_agent():
    time.sleep(0.2)
    
    
def fake_agent():
    e = []
    for i in range(8):
        e.append(fake_agent_agent.remote())

    ray.get(e)