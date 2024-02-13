import argparse
# add the root to sys.path
import sys
sys.path.append('/Users/vinz/Documents/ETH/Do4')

# Do something with the input and output files
from Simulation.plot.read_and_average_csv import read_and_average_csv
from helper import sort_single_dfs, sort_full_dfs, print_result, save_df


def main(road_network, algorithm, num_return):

    data = f"../Simulation_Results/{road_network}/Results/"

    df_single_entry, df_full_entries, meta_info = read_and_average_csv(data, algorithm)


    # Define the desired sorting order for each column
    sorting_order = {
        'Travel Time w Buffer': 'asc',  # Lower is better
        'Travel Time wo Buffer': 'asc',  # Lower is better
        'Waiting Time Per Vehicle': 'asc',  # Lower is better
        'Waiting Time Per Vehicle Max': 'asc',  # Lower is better
        'Number of Stops': 'asc', # Lower is better
        'Number of Vehicles Entered the Network': 'desc', # Higher is better
        'Phase Change Frequency': 'asc' # Lower is better
    }

    result = sort_single_dfs(df_single_entry, sorting_order, num_return)

    print_result(result)

    save_df(result, algorithm, "single")


    # Define the desired sorting order for each column
    sorting_order = {
        'Computation Time': 'asc',  # Lower is better
        'Objective Values': 'asc',  # Higher is better
        'Pressure Values': 'asc',  # Lower is better
        'Throughput': 'desc',  # Higher is better
        'Vehicle Speed': 'desc', # Higher is better
        'Waiting Vehicles Per Intersection': 'asc', # Lower is better
        'Waiting Vehicles Per Lane': 'asc', # Lower is better
        'Waiting Vehicles Per Lane Max': 'asc' # Lower is better
    }


    result = sort_full_dfs(df_full_entries, sorting_order, num_return)

    print_result(result)

    save_df(result, algorithm, "full")
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Comparison Script')
    
    
    parser.add_argument('--road_network', '-rn', type = str)
    parser.add_argument('--algorithm', '-algo', type = str)
    parser.add_argument('--num_return', '-num', type = int)

    args = parser.parse_args()
    
    main(args.road_network, args.algorithm, args.num_return)