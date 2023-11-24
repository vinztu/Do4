import cityflow
import json
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
    
    def __init__(self, dir_config_file, thread_num, params, algorithm):
        self.dir_config_file = dir_config_file
        self.dir_roadnet_file = self.__load_roadnet_file_name()
        self.thread_num = thread_num
        self.engine = cityflow.Engine(dir_config_file, thread_num)
        self.engine.reset()
        
        self.algorithm = algorithm
        self.params = params
        self.perform = self.__define_perform_dict()
        self.lanes_data = None
        self.intersections_data = None
        
        
    # retrieve file name for roadnet file 
    def __load_roadnet_file_name(self):
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