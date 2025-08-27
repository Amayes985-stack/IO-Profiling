import os  # Importing the os module for file and directory management
import sys  # Importing the sys module for handling command-line arguments
import json  # Importing the json module to work with JSON data
import pandas as pd  # Importing pandas for data manipulation and analysis
import matplotlib.pyplot as plt  # Importing matplotlib for plotting

# Function to read a file containing a single timestamp
def read_single_timestamp(filepath):
    with open(filepath, 'r') as f:  # Open the file in read mode
        line = f.readline().strip()  # Read the first line and strip any whitespace
    return line  # Return the timestamp as a string

# Function to load JSON data and filter based on provided timestamps
def load_and_filter_data(read_file, end_file, begin_file):
    # Load the JSON data from the read file
    with open(read_file, 'r') as f:
        data_read = json.load(f)

    # Read the timestamps from the end and begin files
    end_io1_timestamp = read_single_timestamp(end_file)
    begin_io2_timestamp = read_single_timestamp(begin_file)

    # Normalize JSON data into a pandas DataFrame
    df = pd.json_normalize(data_read)
    df['timestamp'] = pd.to_datetime(df['timestamp'])  # Convert the timestamp column to datetime objects
    end_io1_timestamp = pd.to_datetime(end_io1_timestamp)  # Convert end timestamp to datetime
    begin_io2_timestamp = pd.to_datetime(begin_io2_timestamp)  # Convert begin timestamp to datetime

    # Filter the DataFrame to include only rows between the end of IO1 and the beginning of IO2
    df_filtered = df[(df['timestamp'] > end_io1_timestamp) & (df['timestamp'] < begin_io2_timestamp)]
    return df_filtered  # Return the filtered DataFrame

# Verify the number of command-line arguments
if len(sys.argv) != 3:
    print("Usage: python box_plot_io.py <log_dir> <io_size>")
    sys.exit(1)  # Exit the script if the number of arguments is incorrect

# Retrieve command-line arguments
log_dir = sys.argv[1]  # The directory containing log files
io_size = sys.argv[2]  # The size of the IO to be processed

# Define the output directory for the boxplots
boxplot_dir = os.path.join(log_dir, 'box_plot')
os.makedirs(boxplot_dir, exist_ok=True)  # Create the directory if it doesn't exist

# Define the file sizes to be processed
file_sizes = ['256M', '1G', '4G']
dataframes = []  # Initialize an empty list to store DataFrames

# Load and filter data for each file size
for size in file_sizes:
    # Define paths for small and big read files
    read_file_small = os.path.join(log_dir, 'small_size_io', f'READ_{io_size}', f'READ_{size}.json')
    read_file_big = os.path.join(log_dir, 'big_size_io', f'READ_{io_size}', f'READ_{size}.json')

    # Define paths for the end and begin timestamp files
    end_file = os.path.join(log_dir, 'io_timestamp', f'io_end_{io_size}_{size}_iteration_01.json')
    begin_file = os.path.join(log_dir, 'io_timestamp', f'io_begin_{io_size}_{size}_iteration_02.json')

    # Check if the small read file exists and load it, else load the big read file
    if os.path.exists(read_file_small):
        df_filtered = load_and_filter_data(read_file_small, end_file, begin_file)
    elif os.path.exists(read_file_big):
        df_filtered = load_and_filter_data(read_file_big, end_file, begin_file)
    else:
        print(f"Warning: No read file found for size {size}")
        continue  # Skip to the next iteration if no file is found

    # Add a column indicating the file size to the filtered DataFrame
    df_filtered['size'] = size
    dataframes.append(df_filtered)  # Append the filtered DataFrame to the list

# Concatenate all the DataFrames into a single DataFrame
df_all = pd.concat(dataframes)

# Create a boxplot for each file size
plt.figure(figsize=(12, 8))  # Create a figure with specified dimensions
boxplot = df_all.boxplot(column='value', by='size', grid=True, showfliers=False, patch_artist=True)

# Customize the boxplot
colors = ['purple', 'orange', 'green']  # Define colors for the boxplot
for patch, color in zip(boxplot.artists, colors):
    patch.set_facecolor(color)  # Set the fill color of the boxplot
    patch.set_edgecolor('black')  # Set the edge color of the boxplot

# Add labels and a title to the plot
plt.title(f'Boxplot of wattmeter measurement between IO of size {io_size}')
plt.suptitle('')  # Suppress the default title
plt.xlabel('File Size')
plt.ylabel('Watt')
plt.xticks(rotation=0)  # Ensure the x-axis labels are not rotated

# Add a grid to the plot for better readability
plt.grid(True, linestyle='--', linewidth=0.7, alpha=0.7)

# Save the plot to a file
output_file = os.path.join(boxplot_dir, f'boxplot_{io_size}.png')
plt.savefig(output_file)  # Save the plot as a PNG file

# Close the figure to avoid displaying an empty plot
plt.close()

print(f"Boxplot saved to {output_file}")  # Inform the user that the plot has been saved

