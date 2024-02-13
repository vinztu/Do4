# Traffic Signal Controller Simulation

## Introduction

This repository contains a simulation study on traffic signal control using the Maximum Pressure algorithm and the Lyapunov Drift Plus Penalty theory. The study was conducted by vinztu and kenanz0630 and zyhe from ETH Zürich and EPFL Lausanne. The simulation is based on a theoretical analysis presented in our forthcoming paper, ???.

The simulation uses the famous Maximum Pressure algorithm and the Lyapunov Drift Plus Penalty theory to evaluate the performance of different traffic signal control algorithms. The simulation results are compared using sensitivity analysis to analyze the impact of different parameters on the performance of the algorithms.

The code uses CityFlow as a simulation environment (https://cityflow-project.github.io/).

## Folder Structure

The simulation folder is organized as follows:

- **Generator**: This folder contains the code for generating all possible flow.json and roadnet.json files.
- **Algorithms**: This folder contains the implementation of various signal traffic algorithms, including Fixed Time Controller, Maximum Pressure (MP), Capacity-aware MP, Centralized, and LDPP with 2 penalty and 2 consensus algorithms.
- **Comparison**: This folder contains code for comparing simulation results with different parameters, performing sensitivity analysis.
- **Helper**: This folder contains helper functions used in the simulations.
- **Metrics**: This folder records various metrics during the simulation and stores them in a .csv file.
- **Plot**: This folder contains code for plotting the simulation results based on the .csv files.
- **main.ipynb**: This is the main notebook to start the simulation.
- **main.py**: This is the same as main.ipynb but as a Python file.
- **parameter_loader.py**: This file defines various parameters for the simulation for all algorithms.
- **test.ipynb**: This notebook is used for testing road networks.

## Sources

1. Varaiya, Pravin. "Max Pressure Control of a Network of Signalized Intersections." Transportation Research Part C: Emerging Technologies, vol. 36, 2013, pp. 177-195. [source](https://doi.org/10.1016/j.trc.2013.08.014)

2. Neely, Michael J. "Stochastic Network Optimization with Application to Communication and Queueing Systems." Synthesis Lectures on Learning, Networks, and Algorithms, 2010. [source](https://doi.org/10.1007/978-3-031-79995-2)
