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


def plot_single(df_single_entry, meta_info, params, save_fig_info):
    
    # extract all metrics
    first_key = list(df_single_entry.keys())[0]
    all_metrics = df_single_entry[first_key].columns
    
    # create a color map
    clrs = params.Figure.colors(np.linspace(0, 1, len(df_single_entry)))
    
    for metric in all_metrics:
        
        # create a plot with the correct size and color
        fig, ax = plt.subplots(figsize = params.Figure.figsize, facecolor = params.Figure.facecolor, edgecolor = params.Figure.edgecolor, tight_layout=True)
        
        # get unit to metric
        x_label = r"Simulation Time [s]"
        y_label = get_unit(metric)
        
        for i, (algorithm, dataframe) in enumerate(df_single_entry.items()):
            
            # create label naming
            label = label_name(algorithm, meta_info, params)
                
            # extract mean and std info for specific algorithms
            mean = dataframe[metric].loc["mean"]
            std = dataframe[metric].loc["std"]
            
            # plot 1 bar with yerr
            ax.bar(i, mean, yerr=std,
                   align = "center",
                   alpha = params.Plot.alpha,
                   capsize = params.Plot.capsize,
                   label = label,
                   color = clrs[i]
                  )
                
            # set the number above the bar plot
            ax.text(i, (mean + std) * 1.02,
                    s = round(mean, 2),
                    ha = "center",
                    fontsize = params.Plot.text_font_size,
                    fontweight = params.Plot.text_font_weight,
                    fontstyle = params.Plot.text_font_style,
                   )
            
        
        # create the y-label
        set_labels(ax, params, None, y_label, metric, False)
        set_ticks(ax, params, axis = "y")
        set_legend(params, "$\mathbf{Algorithms}$")
        set_grid(ax, params)
        if save_fig_info["save"]:
            save_fig(save_fig_info["save_dir"])
        
        
        plt.show()
        
    
    if save_fig_info["save_legend"]:
        create_separate_legend(ax, params, save_fig_info)
            


