import matplotlib.pyplot as plt

def set_legend(params, title, plot_full = False):
    font_family = {'family': params.Legend.family}
    title_font_family = {'family': params.Legend.family, "size": params.Legend.title_fontsize,}
    leg = plt.legend(loc = params.Legend.loc,
                     frameon = params.Legend.frameone,
                     fontsize = params.Legend.fontsize,
                     title = title,
                     #title_fontsize = params.Legend.title_fontsize,
                     title_fontproperties = title_font_family,
                     bbox_to_anchor = params.Legend.bbox_to_anchor,
                     ncol = params.Legend.ncol,
                     columnspacing = params.Legend.columnspacing,
                     fancybox = params.Legend.fancybox,
                     borderaxespad = params.Legend.borderaxespad,
                     borderpad = params.Legend.borderpad,
                     labelspacing = params.Legend.labelspacing,
                     handlelength = params.Legend.handlelength,
                     prop = font_family
                    )
    
    legend_frame = leg.get_frame()
    legend_frame.set_edgecolor(params.Legend.edgecolor)      # Set frame color
    legend_frame.set_linewidth(params.Legend.linewidth)      # Set frame linewidth
    legend_frame.set_facecolor(params.Legend.facecolor)      # Set background color
    legend_frame.set_alpha(params.Legend.alpha)
    
    for legend_line in plt.gca().get_legend().get_lines():
        legend_line.set_linewidth(params.Legend.graph_linewidth) # set linewidth of the graph indication in the legends