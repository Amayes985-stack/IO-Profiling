import os
import json
import pandas as pd

def convert_json_to_csv(json_file, csv_file):
    # Open the JSON file and load its contents into a Python dictionary
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Convert the dictionary to a Pandas DataFrame for easier manipulation
    df = pd.json_normalize(data)
    
    # Keep only the columns for timestamp and value
    df = df[['timestamp', 'value']]

    # Rename columns to indicate units and format of the data
    df.columns = ['timestamp (format: ISO8601)', 'value (unit: watt)']

    # Save the DataFrame as a CSV file without the index column
    df.to_csv(csv_file, index=False)

if __name__ == "__main__":
    import sys
    # Check if the correct number of arguments is passed
    if len(sys.argv) != 3:
        print("Usage: python format_baseline.py <input_json_file> <output_csv_file>")
        sys.exit(1)

    # Assign input and output file paths from command-line arguments
    input_json_file = sys.argv[1]
    output_csv_file = sys.argv[2]
    
    # Call the function to convert JSON to CSV
    convert_json_to_csv(input_json_file, output_csv_file)

