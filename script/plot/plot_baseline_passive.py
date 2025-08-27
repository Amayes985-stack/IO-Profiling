import sys  # Import the sys module for handling command-line arguments
import os  # Import the os module for interacting with the operating system, such as handling file paths
import json  # Import the json module to parse JSON files
import matplotlib  # Import the matplotlib library for creating plots

matplotlib.use('Agg')  # Set the backend for matplotlib to 'Agg', which is non-interactive and suitable for scripts that generate plots without displaying them
import matplotlib.pyplot as plt  # Import the pyplot module from matplotlib for easy plotting
from dateutil.parser import parse as parse_date  # Import the parse function from dateutil.parser to convert strings into datetime objects

# Function to load data from a JSON file
def load_data(file_path):
    with open(file_path, 'r') as file:  # Open the file in read mode
        data = json.load(file)  # Load the JSON data from the file
    return data  # Return the loaded data

# Function to plot the baseline energy consumption over time
def plot_baseline(baseline_data, log_dir):
    # Convert timestamps from string to datetime objects for plotting
    baseline_timestamps = [parse_date(entry['timestamp']) for entry in baseline_data]
    baseline_watt_values = [entry['value'] for entry in baseline_data]

    # Set up the plot with a specific size (10 inches by 6 inches)
    plt.figure(figsize=(10, 6))
    plt.plot(baseline_timestamps, baseline_watt_values, label='Wattmeter measurements - 15 minutes - Baseline', color='blue')

    # Label the x-axis and y-axis
    plt.xlabel('Time')
    plt.ylabel('Energy Consumption (Watts)')
    
    # Set the title of the plot
    plt.title('Energy Consumption over Time - Baseline')
    
    # Display the legend
    plt.legend()
    
    # Enable grid lines for better readability
    plt.grid(True)
    
    # Rotate the x-axis labels by 45 degrees for better readability
    plt.xticks(rotation=45)
    
    # Adjust layout to prevent clipping of labels
    plt.tight_layout()

    # Create the directory for saving the plot if it doesn't exist
    plot_dir = os.path.join(log_dir, 'plot', 'baseline')
    os.makedirs(plot_dir, exist_ok=True)

    # Define the output path for the plot
    output_path = os.path.join(plot_dir, 'plot_baseline.png')
    
    # Save the plot as a PNG file
    plt.savefig(output_path)
    
    # Close the plot to free up memory and avoid generating an extra empty plot
    plt.close()

    # Print a confirmation message with the output path
    print(f"Plot saved to {output_path}")

# Main function to load the baseline data and create the plot
def main(log_dir):
    # Define the path to the baseline JSON file
    baseline_file = os.path.join(log_dir, 'baseline', 'baseline.json')

    # Check if the baseline file exists
    if not os.path.exists(baseline_file):
        print(f"Error: {baseline_file} does not exist.")
        return

    # Load the baseline data from the JSON file
    baseline_data = load_data(baseline_file)
    
    # Plot the baseline data
    plot_baseline(baseline_data, log_dir)

# Entry point of the script
if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python plot_baseline_passive.py <log_dir>")
        sys.exit(1)
    
    # Get the log directory from the command-line arguments
    log_dir = sys.argv[1]
    
    # Call the main function with the provided log directory
    main(log_dir)

