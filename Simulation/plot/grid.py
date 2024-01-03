def set_grid(ax, params):
    ax.grid(True,
            linewidth = params.Grid.linewidth,
            linestyle=params.Grid.linestyle,
            alpha=params.Grid.alpha)
    
    ax.set_axisbelow(True)  # Ensure grid lines are drawn below other plot elements