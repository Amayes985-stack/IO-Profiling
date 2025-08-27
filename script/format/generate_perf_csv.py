import os
import json
import pandas as pd  # Importing pandas for handling data in DataFrame
from datetime import datetime  # Importing datetime for handling and converting timestamps

def convert_timestamps_to_csv(io_begin_json, io_end_json, output_csv_file, iteration):
    # Read the start timestamps from the JSON file
    with open(io_begin_json, 'r') as f:
        begin_data = f.readlines()  # Reading all lines from the begin timestamp file

    # Read the end timestamps from the JSON file
    with open(io_end_json, 'r') as f:
        end_data = f.readlines()  # Reading all lines from the end timestamp file

    # Check if the number of start and end timestamps match
    if len(begin_data) != len(end_data):
        print(f"Error: Mismatch in number of begin and end timestamps in iteration {iteration}")
        return  # Exit the function if there is a mismatch

    # Create a DataFrame to store the data
    data = []
    for i in range(len(begin_data)):
        # Convert the start timestamp from string to datetime object
        begin_timestamp = datetime.strptime(begin_data[i].strip(), "%Y-%m-%dT%H:%M:%S.%f%z")
        # Convert the end timestamp from string to datetime object
        end_timestamp = datetime.strptime(end_data[i].strip(), "%Y-%m-%dT%H:%M:%S.%f%z")
        # Calculate the duration in seconds
        duration = (end_timestamp - begin_timestamp).total_seconds()
        # Append the data as a list [iteration, begin_timestamp, end_timestamp, duration]
        data.append([iteration, begin_timestamp.isoformat(), end_timestamp.isoformat(), duration])

    # Convert the list of data into a DataFrame
    df = pd.DataFrame(data, columns=['iteration', 'timestamp_begin', 'timestamp_end', 'duration (s)'])

    # Save the DataFrame to a CSV file
    with open(output_csv_file, 'a') as f:
        # Write the DataFrame to the CSV file. The header is written only if the file is empty.
        df.to_csv(f, header=f.tell()==0, index=False)
        f.write('\n\n')  # Add blank lines between iterations for readability

if __name__ == "__main__":
    import sys  # Importing sys for handling command-line arguments
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 5:
        print("Usage: python generate_perf_csv.py <io_begin_json> <io_end_json> <output_csv_file> <iteration>")
        sys.exit(1)  # Exit the script if the number of arguments is incorrect

    # Assigning command-line arguments to variables
    io_begin_json = sys.argv[1]
    io_end_json = sys.argv[2]
    output_csv_file = sys.argv[3]
    iteration = int(sys.argv[4])

    # Call the function to convert timestamps to CSV
    convert_timestamps_to_csv(io_begin_json, io_end_json, output_csv_file, iteration)

