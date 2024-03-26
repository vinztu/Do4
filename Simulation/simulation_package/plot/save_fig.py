import matplotlib.pyplot as plt

def save_fig(dir_name, plot_name):
    plt.savefig(dir_name + "_".join(plot_name.split()) +'.pdf', format='pdf', bbox_inches='tight')