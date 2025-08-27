import sys  # Import the sys module to handle command-line arguments
import os  # Import the os module to interact with the operating system, such as handling file paths
import json  # Import the json module to parse JSON files
import matplotlib  # Import the matplotlib library for creating plots

matplotlib.use('Agg')  # Set the backend for matplotlib to 'Qt5Agg', suitable for generating plots in a non-interactive script
import matplotlib.pyplot as plt  # Import the pyplot module from matplotlib for easy plotting
from dateutil.parser import parse as parse_date  # Import the parse function from dateutil.parser to convert strings into datetime objects

# Function to load data from a JSON file
def load_data(file_path):
    with open(file_path, 'r') as file:  # Open the file in read mode
        data = json.load(file)  # Load the JSON data from the file
    return data  # Return the loaded data

# Function to read all timestamps from a file
def read_all_timestamps(filepath):
    with open(filepath, 'r') as f:  # Open the file in read mode
        lines = f.readlines()  # Read all lines from the file
    return [line.strip() for line in lines]  # Return the lines as a list, with each line stripped of leading/trailing whitespace

# Function to plot the IO energy consumption data
def plot_io(io_data, io_timestamps, log_dir, sz_bloc, filesize):
    # Convert timestamps from string to datetime objects for plotting
    io_timestamps_dt = [parse_date(entry['timestamp']) for entry in io_data]
    io_watt_values = [entry['value'] for entry in io_data]

    # Set up the plot with a specific size (12 inches by 8 inches)
    plt.figure(figsize=(12, 8))
    plt.plot(io_timestamps_dt, io_watt_values, label=f'Wattmeter measurements \n during IO - {sz_bloc}', color='red')

    colors = ['green', 'purple']  # Colors for the vertical lines marking IO start and end times
    for i, (begin, end) in enumerate(io_timestamps):
        color = colors[i % 2]  # Alternate between green and purple
        plt.axvline(x=begin, color=color, linestyle='dashed', linewidth=1, label=f'Start IO {i+1}')
        plt.axvline(x=end, color=color, linestyle='dashed', linewidth=1, label=f'End IO {i+1}')

    plt.xlabel('Time')  # Label for the x-axis
    plt.ylabel('Energy Consumption (Watts)')  # Label for the y-axis
    plt.title(f'Energy Consumption over Time - IO size {sz_bloc} & buffer size {filesize}')  # Title of the plot
    
    # Manually create the legend to ensure proper labeling
    handles, labels = plt.gca().get_legend_handles_labels()
    
    # First legend for the main data line
    legend1 = plt.legend(handles[:1], labels[:1], loc='upper right', bbox_to_anchor=(1.005, 1),
           bbox_transform=plt.gcf().transFigure)
    plt.gca().add_artist(legend1)  # Add the first legend to the plot

    # Second legend for the vertical lines marking IO start and end times
    legend2 = plt.legend(handles[1:], labels[1:], loc='upper right', ncol=1, bbox_to_anchor=(1.005, 0.95),
           bbox_transform=plt.gcf().transFigure)

    plt.grid(True)  # Enable grid lines for better readability
    plt.xticks(rotation=45)  # Rotate the x-axis labels by 45 degrees for better readability
    plt.tight_layout()  # Adjust layout to prevent clipping of labels

    # Create the directory for saving the plot if it doesn't exist
    plot_dir = os.path.join(log_dir, 'plot', sz_bloc)
    os.makedirs(plot_dir, exist_ok=True)

    # Define the output path for the plot
    output_path = os.path.join(plot_dir, f'plot_io_{sz_bloc}_{filesize}_all_run.png')
    
    # Save the plot as a PNG file
    plt.savefig(output_path)
    plt.show()  # Display the plot

    # Print a confirmation message with the output path
    print(f"Plot saved to {output_path}")

# Main function to load data, process timestamps, and plot the IO energy consumption
def main(log_dir, sz_bloc):
    io_sizes = ['256M', '1G', '4G']  # List of file sizes to process
    for filesize in io_sizes:
        # Construct file paths for small and big IO sizes
        read_file_small = os.path.join(log_dir, f'small_size_io/READ_{sz_bloc}/READ_{filesize}.json')
        read_file_big = os.path.join(log_dir, f'big_size_io/READ_{sz_bloc}/READ_{filesize}.json')
        
        if os.path.exists(read_file_small):
            read_file = read_file_small  # Use the small IO size file if it exists
        elif os.path.exists(read_file_big):
            read_file = read_file_big  # Use the big IO size file if it exists
        else:
            print(f"Error: Neither {read_file_small} nor {read_file_big} exists.")  # Error if neither file exists
            continue

        io_data = load_data(read_file)  # Load the IO data from the selected file

        # List all available io_begin and io_end files
        timestamp_dir = os.path.join(log_dir, 'io_timestamp')
        io_begin_files = sorted([f for f in os.listdir(timestamp_dir) if f.startswith(f'io_begin_{sz_bloc}_{filesize}_iteration_')])
        io_end_files = sorted([f for f in os.listdir(timestamp_dir) if f.startswith(f'io_end_{sz_bloc}_{filesize}_iteration_')])

        if len(io_begin_files) != len(io_end_files):
            print(f"Warning: Mismatch in number of begin and end files for size {filesize}")
            continue

        # Read the timestamps from all files
        begin_timestamps = [read_all_timestamps(os.path.join(timestamp_dir, f)) for f in io_begin_files]
        end_timestamps = [read_all_timestamps(os.path.join(timestamp_dir, f)) for f in io_end_files]

        # Flatten the lists of lists into single lists
        begin_timestamps = [ts for sublist in begin_timestamps for ts in sublist]
        end_timestamps = [ts for sublist in end_timestamps for ts in sublist]

        if len(begin_timestamps) != len(end_timestamps):
            print(f"Warning: Mismatch in number of begin and end timestamps for size {filesize}")
            continue

        io_timestamps = list(zip(begin_timestamps, end_timestamps))  # Pair up the begin and end timestamps

        # Convert timestamps to datetime objects
        io_timestamps = [(parse_date(begin), parse_date(end)) for begin, end in io_timestamps]

        # Plot the energy consumption data
        plot_io(io_data, io_timestamps, log_dir, sz_bloc, filesize)

# Entry point of the script
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python plot_io_all_run.py <log_dir> <sz_bloc>")
        sys.exit(1)
    
    log_dir = sys.argv[1]  # Get the log directory from the command-line arguments
    sz_bloc = sys.argv[2]  # Get the block size from the command-line arguments
    main(log_dir, sz_bloc)  # Call the main function with the provided arguments

