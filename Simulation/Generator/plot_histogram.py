import numpy as np
import matplotlib.pyplot as plt

def plot_distribution(routes_dict, num_vehicles):
    num_plots = len(num_vehicles)
    num_cols = 2
    num_rows = (num_plots + num_cols - 1) // num_cols
    
    # Define the bucket size
    bucket_size = 50

    # Calculate the number of bins based on the bucket size
    num_bins = int((max(max(values) for values in num_vehicles.values()) + bucket_size) / bucket_size)
    
    vehicles_per_hour = 0
    for values in num_vehicles.values():
        vehicles_per_hour += len(np.array(values)[np.array(values) < 3600])

    # Create the subplots
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(12, 8))
    
    # total frequencies and bins
    total_frequencies = {}
    total_bins = {}

    # Plot the distribution for each key
    for (key, values), ax in zip(num_vehicles.items(), axes.flatten()):
        frequencies, bins, _ = ax.hist(values, bins=num_bins, alpha=0.9)
        ax.set_title(key)
        ax.grid(alpha = 0.7)
        
        total_frequencies[key] = frequencies
        total_bins[key] = bins

    # Remove any empty subplots
    if num_plots < num_rows * num_cols:
        for ax in axes.flatten()[num_plots:]:
            ax.axis('off')

    # Adjust the layout
    plt.tight_layout()
    
    fig.suptitle(f"Total Vehicles per hour: {vehicles_per_hour} veh/h", fontsize=12, fontweight='bold')
    plt.subplots_adjust(top=0.9)

    # Display the plot
    plt.show()
    
    return total_frequencies, total_bins