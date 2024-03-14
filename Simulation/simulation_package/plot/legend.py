import matplotlib.pyplot as plt

def set_legend(params, title):
    leg = plt.legend(loc = params.Legend.loc,
                     frameon = params.Legend.frameone,
                     fontsize = params.Legend.fontsize,
                     title = title,
                     title_fontsize = params.Legend.title_fontsize,
                     bbox_to_anchor = params.Legend.bbox_to_anchor,
                     ncol = params.Legend.ncol,
                     fancybox = params.Legend.fancybox,
                     borderaxespad = params.Legend.borderaxespad,
                     borderpad = params.Legend.borderpad,
                     labelspacing = params.Legend.labelspacing,
                     handlelength = params.Legend.handlelength
                    )
    
    legend_frame = leg.get_frame()
    legend_frame.set_edgecolor(params.Legend.edgecolor)      # Set frame color
    legend_frame.set_linewidth(params.Legend.linewidth)      # Set frame linewidth
    legend_frame.set_facecolor(params.Legend.facecolor)      # Set background color
    legend_frame.set_alpha(params.Legend.alpha)