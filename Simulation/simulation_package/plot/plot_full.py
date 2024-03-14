import matplotlib.pyplot as plt
import numpy as np

from units import get_unit
from labels import set_labels
from ticks import set_ticks
from legend import set_legend
from grid import set_grid
from save_fig import save_fig
from label_name import label_name
from separate_legend import create_separate_legend


def plot_full(df_full_entries, meta_info, params, save_fig_info):
    
    # extract all metrics
    first_algorithm = list(df_full_entries.keys())[0]
    all_metrics = df_full_entries[first_algorithm]["mean"].columns
    
    # create a color map
    clrs = params.Figure.colors(np.linspace(0, 1, len(df_full_entries)))
    
    for metric in all_metrics:
        
        if metric == "Number Consensus Iterations":
            continue
        
        # create a plot with the correct size and color
        fig, ax = plt.subplots(figsize = params.Figure.figsize, facecolor = params.Figure.facecolor, edgecolor = params.Figure.edgecolor, tight_layout=True)
        
        # get unit to metric
        x_label = r"Simulation Time [s]"
        y_label = get_unit(metric)
        
        for i, (algorithm, dataframe) in enumerate(df_full_entries.items()):
            
            # create label naming
            label = label_name(algorithm, meta_info, params)
                
            # extract mean and std info for specific algorithms
            mean = dataframe["mean"][metric]
            std = dataframe["std"][metric]
            
            plt.errorbar(dataframe.index, mean,
                         fmt = params.Plot.fmt,
                         mec = params.Plot.mec,
                         ms = params.Plot.ms,
                         linewidth = params.Plot.linewidth,
                         label = label,
                         color = clrs[i])
            
            

        set_labels(ax, params, x_label, y_label, metric, True)
        set_ticks(ax, params)
        set_legend(params, "$\mathbf{Algorithms}$")
        set_grid(ax, params)
        if save_fig_info["save"]:
            save_fig(save_fig_info["save_dir"])
        
        
        plt.show()
        
    
    if save_fig_info["save_legend"]:
        create_separate_legend(ax, params, save_fig_info)
            


