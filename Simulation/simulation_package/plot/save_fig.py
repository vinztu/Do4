import matplotlib.pyplot as plt

def save_fig(dir_name, plot_name):
    plt.savefig(dir_name + plot_name +'.pdf', bbox_inches='tight')