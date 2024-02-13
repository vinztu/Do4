import pandas as pd
import numpy as np
from itertools import takewhile
from os import listdir
import ast


def read_and_average_csv(complete_dir, selective_algorithm = False):
    """ with selective_algorithm one can decide to only look at results from a specific algorithm (e.g. MP, Centralized, LDPP-G, ...) """
    
    # create empty dictionaries to store the results
    meta_info = {}
    df_single_entry = {}
    df_full_entries = {}


    for algorithm in sorted(listdir(complete_dir)):

        # filter out other directories
        if algorithm.startswith(".") or algorithm.startswith("Plots"):
            continue
            
        if selective_algorithm:
            alg = algorithm.split("_")[0]
            if not alg.startswith(selective_algorithm):
                continue
            

        # directory with all results for that algorithm
        algorithm_results = complete_dir + algorithm

        # all simulation files
        simulation_runs = listdir(algorithm_results)
        

        # extract meta information (same for each file in a dir)
        with open(algorithm_results + "/" + simulation_runs[0], "r") as f:
                # takewhile returns an iterator over all the lines 
                # that start with the comment string
                headiter = takewhile(lambda s: s.startswith('#'), f)

                # Extract the dictionary from the header
                m_i = ast.literal_eval(next(headiter).strip("# \n"))
                meta_info[algorithm] = m_i

        # store all df for 1 algorithm, such that we can calculate the average and std later
        df_full_entries_temp = []
        df_single_entries_temp = []


        for sim_run in simulation_runs:

            whole_df = pd.read_csv(algorithm_results + "/" + sim_run, comment = "#")

            # Separate dataframe with columns having entries for each time step
            df_fe = whole_df.dropna(axis=1, how='any')
            df_full_entries_temp.append(df_fe)

            # Separate dataframe with columns having only one entry (or NaN)
            single_entry_cols = whole_df.columns[(whole_df.notnull().sum() <= 1)]
            df_se = whole_df[single_entry_cols].dropna(axis=0)
            df_single_entries_temp.append(df_se)


        # take the avarage and standard deviation
        concat_se = pd.concat([df for df in df_single_entries_temp])
        concat_fe = pd.concat([df for df in df_full_entries_temp])

        df_single_entry[algorithm] = pd.DataFrame([concat_se.mean(), concat_se.std()], index = ["mean", "std"])
        df_full_entries[algorithm] = concat_fe.pivot_table(index = "Time", aggfunc=["mean", "std"])
        
    return df_single_entry, df_full_entries, meta_info