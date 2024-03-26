def set_labels(ax, params, xlabel, ylabel, title, save_fig_info):
    # Set title and labels
    ax.set_ylabel(ylabel,
                  ha='center',
                  va='center',
                  labelpad=params.Labels.labelpad,
                  fontsize=params.Labels.fontsize,
                  fontweight=params.Labels.fontweight,
                  family=params.Labels.family
                 )
    
    # not used for certain plots
    if xlabel is not None:
        ax.set_xlabel(xlabel,
                      ha='center',
                      va='center',
                      labelpad=params.Labels.labelpad,
                      fontsize=params.Labels.fontsize,
                      fontweight=params.Labels.fontweight,
                      family=params.Labels.family
                     )
    
    if not save_fig_info["save"]:
        ax.set_title(title,
                     ha='center',
                     va='center',
                     fontsize=params.Title.fontsize,
                     pad=params.Title.pad,
                     fontweight=params.Title.fontweight,
                     family=params.Title.family)