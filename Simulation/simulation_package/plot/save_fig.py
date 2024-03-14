import matplotlib.pyplot as plt

def save_fig(dir_name):
    plt.savefig(f'{dir_name}.pdf', bbox_inches='tight')