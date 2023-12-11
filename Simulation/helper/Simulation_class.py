import cityflow
import json
import os
from collections import defaultdict

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
    
    def __init__(self, params, algorithm):
        self.dir_config_file = params["dir_config_file"]
        self.dir_roadnet_file = self.__load_roadnet_file_name()
        self.thread_num = params["thread_num"]
        self.engine = cityflow.Engine(self.dir_config_file, self.thread_num)
        self.engine.reset()
        
        self.algorithm = algorithm
        self.params = params
        self.perform = self.__define_perform_dict()
        self.lanes_data = None # will be defind in initialization.py
        self.intersections_data = None # will be defind in initialization.py
        
        self.__ray_environment()
        self.__gurobi_environment()
        
        
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
        
        ray_needed = ["MP", "CA_MP"]
        
        if self.algorithm in ray_needed:
            import ray

            # Initialize ray to enable parallel computing
            ray.init(runtime_env={
                #'excludes': ['/Users/vinz/Documents/ETH/Do4/Simulation/CityFlow/examples/test/replay.txt'],
                #"working_dir": "./",
                "env_vars": {"PYTHONPATH":'/Users/vinz/Documents/ETH/Do4'},
            })

            num_cpu = os.cpu_count()
            print(f"Number of CPUs in this system: {num_cpu}")
    
    
    def __gurobi_environment(self):
        
        # list of all algorithms that need gurobi
        gurobi_needed = ["Centralized", "LDPP"]
        
        if self.algorithm in gurobi_needed:
            import gurobipy as gp
            from gurobipy import GRB

            # define the gurobi environment if needed
            self.gurobi_env = gp.Env(empty=True) # Define gurobi optimization environment
            self.gurobi_env.setParam("OutputFlag",0) # suppress gurobi optimization info
            self.gurobi_env.start()