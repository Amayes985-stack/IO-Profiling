import pandas as pd  # Import the pandas library for data manipulation and analysis
import matplotlib.pyplot as plt  # Import the matplotlib library for plotting graphs
import numpy as np  # Import the numpy library for numerical operations
import sys  # Import the sys library to handle command-line arguments

# Function to calculate the mean energy between 'begin_energy (J)' and 'end_energy (J)'
def calculate_mean_energy(begin_energy, end_energy):
    return (begin_energy + end_energy) / 2

# Function to plot energy differences based on the provided energy and performance data
def plot_energy_difference(energy_filepath, perf_filepath, output_prefix):
    # Load energy data and performance data from their respective CSV files
    energy_data = pd.read_csv(energy_filepath)
    energy_data['timestamp'] = pd.to_datetime(energy_data['timestamp'])

    perf_data = pd.read_csv(perf_filepath)
    perf_data['timestamp_begin'] = pd.to_datetime(perf_data['timestamp_begin'])
    perf_data['timestamp_end'] = pd.to_datetime(perf_data['timestamp_end'])

    # Filter rows where 'begin_energy (J)' is less than 'end_energy (J)'
    perf_data = perf_data[perf_data['begin_energy (J)'] < perf_data['end_energy (J)']]

    # Calculate the delta for each row based on the difference between the measured energy and the mean energy
    perf_data['delta'] = perf_data.apply(lambda row: abs(row['begin_energy (J)'] - row['end_energy (J)']) - calculate_mean_energy(row['begin_energy (J)'], row['end_energy (J)']), axis=1)

    # Select the row with the largest delta where the mean energy is above the projection
    above_projection = perf_data[perf_data['energy_mean (J)'] > perf_data['end_energy (J)']]
    if not above_projection.empty:
        max_delta_above = above_projection.loc[above_projection['delta'].idxmax()]
    else:
        max_delta_above = None

    # Select the row with the largest delta where the mean energy is below the projection
    below_projection = perf_data[perf_data['energy_mean (J)'] < perf_data['end_energy (J)']]
    if not below_projection.empty:
        max_delta_below = below_projection.loc[below_projection['delta'].idxmax()]
    else:
        max_delta_below = None

    # Select the row where the delta is closest to zero
    zero_delta_row = perf_data.iloc[(perf_data['delta'] - 0).abs().argsort()[:1]].iloc[0]

    # Filter to ensure the selected rows are distinct
    rows_to_plot = [row for row in [max_delta_above, max_delta_below, zero_delta_row] if row is not None]

    for index, row in enumerate(rows_to_plot):
        timestamp_begin = row['timestamp_begin']
        timestamp_end = row['timestamp_end']
        begin_energy = row['begin_energy (J)']
        end_energy = row['end_energy (J)']
        mean_energy = calculate_mean_energy(begin_energy, end_energy)

        # Find the timestamps in energy_data that encapsulate the IO operation
        A = energy_data[energy_data['timestamp'] <= timestamp_begin].iloc[-1]
        B = energy_data[energy_data['timestamp'] >= timestamp_end].iloc[0]

        # Add a margin around the timestamps to widen the displayed range
        margin = pd.Timedelta(minutes=0.001)
        filtered_energy_data = energy_data[(energy_data['timestamp'] >= (A['timestamp'] - margin)) & (energy_data['timestamp'] <= (B['timestamp'] + margin))]

        # Create the plot
        fig, ax = plt.subplots()

        # Plot the energy consumption over time (filtered data) in red
        ax.plot(filtered_energy_data['timestamp'], filtered_energy_data['value (Watt)'], color='red', alpha=0.5)

        # Add vertical lines to encapsulate the IO operation
        ax.axvline(x=A['timestamp'], color='blue', linestyle='-', linewidth=2, label='Encadrement Begin')
        ax.axvline(x=B['timestamp'], color='blue', linestyle='-', linewidth=2, label='Encadrement End')

        # Plot the black line between the encapsulating points
        ax.plot([A['timestamp'], B['timestamp']], [A['value (Watt)'], B['value (Watt)']], 'o-', color='black', label='Measured Energy between Encadrement')

        # Calculate the projection of the IO energy on the black line
        projection_timestamp = timestamp_end
        # Calcul de la fraction [0…1] correspondant à la position de projection
        fraction = (
            (projection_timestamp - A['timestamp']).total_seconds()
            / (B['timestamp'] - A['timestamp']).total_seconds()
        )
        # Interpolation linéaire correcte entre EA et EB
        projection_energy = A['value (Watt)'] + (B['value (Watt)'] - A['value (Watt)']) * fraction

        #projection_energy = A['value (Watt)'] + (B['value (Watt)']) * (projection_timestamp - A['timestamp']).total_seconds() / (B['timestamp'] - A['timestamp']).total_seconds()


        # Add the red cross at the projection point
        ax.plot(projection_timestamp, projection_energy, 'x', color='red', label='Projection of IO Energy')

        # Add magenta dashed line from projection point to x-axis
        ax.vlines(
            x=projection_timestamp,
            ymin=0,
            ymax=projection_energy,
            colors='#FF00FF',  # Code hexadécimal pour magenta vif
            linestyles=':',
            linewidth=1.5,
            label='Timestamp of IO End'
        )

        # Add text annotation on x-axis with rotated label
        ax.annotate(
            f'IO End\n{projection_timestamp.strftime("%H:%M:%S.%f")[:-3]}',
            xy=(projection_timestamp, 0),
            xytext=(0, -15),  # Décalage de 15 points vers le bas
            textcoords='offset points',
            ha='center',
            va='top',
            color='#FF00FF',
            fontsize=8,
            arrowprops=dict(arrowstyle="->", color='#FF00FF', lw=1)
        )

        # Ajuster les limites Y pour garder le texte visible
        current_ylim = ax.get_ylim()
        ax.set_ylim(bottom=min(current_ylim[0], 0.8 * current_ylim[1]))  # Ajouter un peu d'espace en bas

        # Add a green dot for the mean energy point
        ax.plot(projection_timestamp, mean_energy, 'o', color='green', label='Mean Energy Point')


        # Add labels, title, and legend
        ax.set_xlabel('Timestamp')
        ax.set_ylabel('Energy (Watt)')
        ax.set_title(f'Energy Consumption Over Time with IO Timestamps - Plot {index+1}')
        ax.legend()

        # Improve presentation
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Set the figure size in inches (8 x 6 inches)
        fig.set_size_inches(8, 6)

        # Save the plot as an SVG file
        plt.savefig(f'{output_prefix}_{index}.svg', format='svg', dpi=300)
        plt.show()

        print(f"Graph saved as '{output_prefix}_{index}.svg'")

# Main entry point of the script
if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 4:
        print("Usage: python plot_delta.py <energy_filepath> <perf_filepath> <output_prefix>")
        sys.exit(1)

    # Get the file paths and output prefix from the command-line arguments
    energy_filepath = sys.argv[1]
    perf_filepath = sys.argv[2]
    output_prefix = sys.argv[3]

    # Call the function to plot the energy differences
    plot_energy_difference(energy_filepath, perf_filepath, output_prefix)

