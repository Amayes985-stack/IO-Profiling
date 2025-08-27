import pandas as pd  # Import the pandas library for data manipulation
import sys  # Import the sys library to handle command-line arguments

# Function to calculate the mean energy between 'begin_energy (J)' and 'end_energy (J)'
def calculate_energy_mean(perf_filepath):
    # Read the performance CSV file into a DataFrame
    perf_data = pd.read_csv(perf_filepath)

    # Calculate the mean energy and add it as a new column 'energy_mean (J)'
    perf_data['energy_mean (J)'] = (perf_data['begin_energy (J)'] + perf_data['end_energy (J)']) / 2

    # Save the updated DataFrame back to the original CSV file
    perf_data.to_csv(perf_filepath, index=False)
    print(f"Energy mean added to {perf_filepath}")

# Main entry point of the script
if __name__ == "__main__":
    # Check if the script is called with the correct number of arguments
    if len(sys.argv) != 2:
        print("Usage: python calculate_energy_mean.py <perf_filepath>")
        sys.exit(1)

    # Get the performance file path from the command-line argument
    perf_filepath = sys.argv[1]

    # Call the function to calculate and add the energy mean to the CSV file
    calculate_energy_mean(perf_filepath)

