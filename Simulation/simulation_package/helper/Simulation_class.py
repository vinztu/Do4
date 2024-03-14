import cityflow
import json
import os
from collections import defaultdict
import numpy as np

class Simulation:
    """
    A class for the simulation.

    ...

    Attributes
    ----------
    dir_config_file : str
        path to the config file for the simulation
    dir_roadnet_file : str
        path to the roadnet file for the simulation
    thread_num : int, optional
        number of threads
    engine : cityflow engine
        the engine class from cityflow
        
    algorithm : str
        Name of the used algorithm for the simulation (MP, ...)
    params : dict
        parameter in the simulation
    lanes_data : dict
        key: lane_id // values: [intersection_id, movement_id, upstream lanes, downstream lanes]
    intersections_data : key: intersection_id // values: {"inflow": [inflowing lanes], "outflow": [outflowing lanes], "neighbours": [all neighbouring intersections]

    Methods
    -------
    sim_step():
        Continue the simulation for n_steps        
    """
    
    def __init__(self, params, algorithm, write_phase_to_json):
        self.dir_config_file = params["dir_config_file"]
        self.dir_roadnet_file = self.__load_roadnet_file_name()
        self.thread_num = params["thread_num"]
        self.write_phase_to_json = write_phase_to_json
        self.engine = cityflow.Engine(self.dir_config_file, self.thread_num)
        self.engine.reset()
        
        self.algorithm = algorithm
        self.params = params
        self.perform = self.__define_perform_dict()
        self.lanes_data = None # will be defind in initialization.py
        self.intersections_data = None # will be defind in initialization.py
        
        self.__ray_environment()
        self.__gurobi_environment()
        
        
    def reset_variables(self, current_round):
        
        self.engine.reset()
        self.perform = self.__define_perform_dict()

        # delete the content of the replay_roadnet.json and replay.txt file
        with open(self.dir_config_file, "r") as f:
            config = json.load(f)

        path = self.dir_config_file.rstrip("config.json")
        replay = config["replayLogFile"]

        # delete the content
        open(path + replay, 'w').close()
        
        
        if "LDPP-T" in self.algorithm:
            self.params["phase_history"] = {intersection: np.ones(self.params["L"])*(-1) for intersection in self.intersections_data}
            self.params["num_consensus_iterations"] = []
            
        elif "LDPP-GF" in self.algorithm:
            self.params["num_consensus_iterations"] = []

   
        
    def __load_roadnet_file_name(self):
        """ retrieve file name for roadnet file """
        with open(self.dir_config_file, 'r') as f:
            data = json.load(f)
            return "./" + data["dir"] + data["roadnetFile"]
        
        
    def __define_perform_dict(self):
        # simulation values (used for performance metrics)
        # for MP, current_pressure == current_objective these values are the same
        perform = {
            "current_pressure": defaultdict(float),   # dict with all pressures for intersections
            "current_objective": defaultdict(float),  # dict with all objectives for intersections
            "current_phase" : defaultdict(int)        # dict with all current activates phases for intersections
        }
        
        return perform
    
    
    def __ray_environment(self):
        
        if self.algorithm != "Centralized":
            import ray

            ray.init()
            
            print('''This cluster consists of
                {} nodes in total
                {} CPU resources in total
            '''.format(len(ray.nodes()), ray.cluster_resources()['CPU']))
            
            self.cpu = int(ray.cluster_resources()['CPU'])

    
    
    def __gurobi_environment(self):
        
        # list of all algorithms that need gurobi (not done for LDPP, since it cannot be serialized for ray --> env defined in LDPP_helper)
        gurobi_needed = ["Centralized"]
        
        if self.algorithm in gurobi_needed:
            import gurobipy as gp
            from gurobipy import GRB

            # define the gurobi environment if needed
            self.gurobi_env = gp.Env(empty=True) # Define gurobi optimization environment
            self.gurobi_env.setParam("OutputFlag",0) # suppress gurobi optimization info
            self.gurobi_env.start()