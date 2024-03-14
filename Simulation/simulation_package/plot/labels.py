def set_labels(ax, params, xlabel, ylabel, title, x_label = True):
    # Set title and labels
    ax.set_ylabel(ylabel,
                  ha='center',
                  va='center',
                  labelpad=params.Labels.labelpad,
                  fontsize=params.Labels.fontsize,
                  fontweight=params.Labels.fontweight)
    
    # not used for certain plots
    if x_label:
        ax.set_xlabel(xlabel,
                      ha='center',
                      va='center',
                      labelpad=params.Labels.labelpad,
                      fontsize=params.Labels.fontsize,
                      fontweight=params.Labels.fontweight)
    
    ax.set_title(title,
                 ha='center',
                 va='center',
                 fontsize=params.Title.fontsize,
                 pad=params.Title.pad,
                 fontweight=params.Title.fontweight)