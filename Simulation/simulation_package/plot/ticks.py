import matplotlib.ticker as ticker
    
def set_ticks(ax, params, axis = 'both'):
    # Set minor tick sizes and label sizes
    ax.tick_params(axis=axis, which='minor',
                   width=params.Ticks.minor_width,
                   length=params.Ticks.minor_length,
                   direction=params.Ticks.direction,
                   pad=params.Ticks.minor_pad,
                   labelsize=params.Ticks.labelsize,
                   labelcolor=params.Ticks.labelcolor)

    # Set major tick sizes and label sizes
    ax.tick_params(axis=axis, which='major',
                   width=params.Ticks.major_width,
                   length=params.Ticks.major_length,
                   direction=params.Ticks.direction,
                   pad=params.Ticks.major_pad,
                   labelsize=params.Ticks.labelsize,
                   labelcolor=params.Ticks.labelcolor)

    
    # Remove minor tick y-labels
    ax.yaxis.set_minor_formatter(ticker.NullFormatter())
    # Set major and minor tick locators
    ax.yaxis.set_major_locator(ticker.AutoLocator())
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator(n=params.Ticks.number_minor))  # Adjust n to control the number of minor ticks
    
    if axis == 'both':
        ax.xaxis.set_minor_formatter(ticker.NullFormatter())
        ax.xaxis.set_major_locator(ticker.AutoLocator())
        ax.xaxis.set_minor_locator(ticker.AutoMinorLocator(n=params.Ticks.number_minor)) # Adjust n to control the number of minor ticks
    elif axis == 'y':
        ax.set_xticks([])
        ax.set_xticklabels([])
        
        