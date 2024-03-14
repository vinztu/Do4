import pandas as pd
import numpy as np
from collections import defaultdict


def sort_single_dfs(dfs, sorting_order, num_return = 3):
    # Perform the comparison for each column
    result = {}
    columns = dfs[list(dfs.keys())[0]].columns

    for col in columns:
        if sorting_order[col] == 'asc':
            sorted_algorithms = sorted(dfs.keys(), key=lambda x: dfs[x][col].values[0])[:num_return]
        elif sorting_order[col] == 'desc':
            sorted_algorithms = sorted(dfs.keys(), key=lambda x: dfs[x][col].values[0], reverse=True)[:num_return]
        result[col] = [(alg, round(dfs[alg][col].loc["mean"], 2), round(dfs[alg][col].loc["std"], 2)) for alg in sorted_algorithms]
        
    return result

def sort_full_dfs(dfs, sorting_order, num_return = 3):
    # Perform the comparison for each column
    result = defaultdict(list)
    columns = dfs[list(dfs.keys())[0]]["mean"].columns

    for col in columns:
        if sorting_order[col] == 'asc':
            sorted_algorithms = sorted(dfs.keys(), key=lambda x: np.mean(dfs[x]["mean"][col]))[:num_return]
        elif sorting_order[col] == 'desc':
            sorted_algorithms = sorted(dfs.keys(), key=lambda x: np.mean(dfs[x]["mean"][col]), reverse=True)[:num_return]
            
        
        for alg in sorted_algorithms:
            mean_of_mean = round(np.mean(dfs[alg]["mean"][col]), 2)
            std_of_mean = round(np.std(dfs[alg]["mean"][col]), 2)

            if "std" in dfs[alg]:
                mean_of_std = round(np.mean(dfs[alg]["std"][col]), 2)
                std_of_std = round(np.std(dfs[alg]["std"][col]), 2)
                result[col].append((alg, mean_of_mean, std_of_mean, mean_of_std, std_of_std))
                
            else:
                result[col].append((alg, mean_of_mean, std_of_mean))

    return result


def print_result(result):
    # Print the results
    for col, algorithms in result.items():
        print(f"Top 3 algorithms for {col}:")
        for val in algorithms:
            if len(val) == 3:
                alg, mean, std = val
                print(f"Algorithm: {alg}, mean: {mean}, std: {std}")
                
            if len(val) == 5:
                alg, mean_of_mean, std_of_mean, mean_of_std, std_of_std = val
                print(f"Algorithm: {alg}, mean_of_mean: {mean_of_mean}, std_of_mean: {std_of_mean}, mean_of_std: {mean_of_std}, std_of_std: {std_of_std}")
        print()
        
        
def save_df(result, algorithm, name):
    # Create a DataFrame from the results
    df_result = pd.DataFrame(result)

    # Save the DataFrame to a CSV file
    df_result.to_csv(f'{algorithm}_{name}_algorithm_comparison.csv', index=False)