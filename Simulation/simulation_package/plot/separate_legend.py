def create_separate_legend(ax, params, save_fig_info):
    fig_leg = plt.figure(figsize=params.Figure.figsize)
    ax_leg = fig_leg.add_subplot(111)
    
    # add the legend from the previous axes
    leg = ax_leg.legend(*ax.get_legend_handles_labels(),
                        loc = "center",
                        frameon = params.Legend.frameone,
                        fontsize = params.Legend.fontsize,
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
    
    # hide the axes frame and the x/y labels
    ax_leg.axis('off')
    fig_leg.savefig(f'{save_fig_info["save_dir"]}_legend.pdf', bbox_inches='tight')