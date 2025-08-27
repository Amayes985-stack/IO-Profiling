import os
import json
import pandas as pd

# Function to convert a JSON file to a CSV file
def convert_json_to_csv(json_file, csv_file):
    # Open and read the JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)

    # Convert the JSON data to a DataFrame
    df = pd.json_normalize(data)
    
    # Keep only the 'timestamp' and 'value' columns from the DataFrame
    df = df[['timestamp', 'value']]
    
    # If the output CSV file is related to energy data, rename the 'value' column
    if "energy" in csv_file:
        df.rename(columns={"value": "value (Watt)"}, inplace=True)
        
    # Save the DataFrame as a CSV file
    df.to_csv(csv_file, index=False)

# Main function to handle command-line arguments
if __name__ == "__main__":
    import sys
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python wattmeter_format.py <input_json_file> <output_csv_file>")
        sys.exit(1)

    # Get the input JSON file and output CSV file from the arguments
    input_json_file = sys.argv[1]
    output_csv_file = sys.argv[2]
    
    # Call the function to convert the JSON file to a CSV file
    convert_json_to_csv(input_json_file, output_csv_file)

