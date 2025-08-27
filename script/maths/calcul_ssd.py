import os
import pandas as pd
from datetime import datetime
import sys

# Function to read a CSV file and return it as a DataFrame
def read_csv_file(filepath):
    return pd.read_csv(filepath)

# Function to parse a timestamp from a string to a datetime object
def parse_timestamp(timestamp):
    try:
        return datetime.fromisoformat(str(timestamp))
    except Exception as e:
        print(f"Error parsing timestamp {timestamp}: {e}")
        raise

# Function to calculate the energy consumed during an IO operation based on timestamps
def calculate_energy_for_io(begin, end, energy_data):
    # Parse the beginning and end timestamps
    begin_dt = parse_timestamp(begin)
    end_dt = parse_timestamp(end)
    
    # Find the closest energy measurement just before the begin timestamp
    A = energy_data[energy_data['timestamp'] <= begin_dt].iloc[-1]
    # Find the closest energy measurement just after the end timestamp
    B = energy_data[energy_data['timestamp'] >= end_dt].iloc[0]
    
    # Calculate the slope (a) and intercept (b) of the line between these two points
    a = (B['value (Watt)'] - A['value (Watt)']) / (B['timestamp'] - A['timestamp']).total_seconds()
    b = A['value (Watt)'] - a * A['timestamp'].timestamp()
    
    # Calculate the energy at the begin and end timestamps using the linear approximation
    begin_energy = a * begin_dt.timestamp() + b
    end_energy = a * end_dt.timestamp() + b

    # Return the energy at the start and end of the IO operation
    return begin_energy, end_energy

# Function to process both energy and performance data files
def process_files(energy_filepath, perf_filepath):
    # Read the energy and performance data files
    energy_data = read_csv_file(energy_filepath)
    perf_data = read_csv_file(perf_filepath)

    # Convert the timestamp columns in the energy data to datetime objects
    energy_data['timestamp'] = pd.to_datetime(energy_data['timestamp'], format='ISO8601')
    # Convert the timestamp columns in the performance data to strings (if necessary)
    perf_data['timestamp_begin'] = perf_data['timestamp_begin'].astype(str)
    perf_data['timestamp_end'] = perf_data['timestamp_end'].astype(str)

    # Initialize lists to store calculated energy values
    begin_energies = []
    end_energies = []

    # Iterate over each row in the performance data
    for index, row in perf_data.iterrows():
        try:
            print(f"Processing row {index} with begin {row['timestamp_begin']} and end {row['timestamp_end']}")
            # Calculate the energy consumption for this IO operation
            begin_energy, end_energy = calculate_energy_for_io(row['timestamp_begin'], row['timestamp_end'], energy_data)
            # Append the calculated values to the lists
            begin_energies.append(begin_energy)
            end_energies.append(end_energy)
        except Exception as e:
            # Handle any errors and append None to indicate failure
            print(f"Error processing row {index}: {e}")
            begin_energies.append(None)
            end_energies.append(None)

    # Add the calculated energies to the performance DataFrame
    perf_data['begin_energy (J)'] = begin_energies
    perf_data['end_energy (J)'] = end_energies

    # Save the updated performance data back to the file
    perf_data.to_csv(perf_filepath, index=False)
    print(f"Updated perf data saved to {perf_filepath}")

# Main function to iterate through directories and process files
def main(base_dir):
    # Loop over the IO types: small and big size IO
    for io_type in ['small_size_io', 'big_size_io']:
        io_dir = os.path.join(base_dir, io_type)
        # Loop over the different IO sizes
        for io_size in os.listdir(io_dir):
            io_size_dir = os.path.join(io_dir, io_size)
            # Loop over the access patterns: random (RAND) and sequential (SEQ)
            for access_pattern in ['RAND', 'SEQ']:
                access_dir = os.path.join(io_size_dir, access_pattern)
                # Loop over the file sizes
                for file_size in ['256M', '1G', '4G']:
                    # Construct the paths for the energy and performance files
                    energy_dir = os.path.join(access_dir, file_size, 'energy')
                    perf_dir = os.path.join(access_dir, file_size, 'perf')

                    energy_filepath = os.path.join(energy_dir, 'data.csv')
                    perf_filepath_pattern = os.path.join(perf_dir, f'perf_{access_pattern}_buffer{file_size}_io{io_size}.csv')

                    # If both energy and performance files exist, process them
                    if os.path.exists(energy_filepath):
                        if os.path.exists(perf_filepath_pattern):
                            print(f"Processing {perf_filepath_pattern} and {energy_filepath}")
                            process_files(energy_filepath, perf_filepath_pattern)
                        else:
                            print(f"Perf file not found: {perf_filepath_pattern}")
                    else:
                        print(f"Energy file not found: {energy_filepath}")

# Entry point of the script
if __name__ == "__main__":
    # Check that the correct number of arguments have been provided
    if len(sys.argv) != 2:
        print("Usage: python calc.py <base_directory>")
        sys.exit(1)

    # Get the base directory from the command-line arguments
    base_directory = sys.argv[1]
    # Call the main function with the base directory
    main(base_directory)

