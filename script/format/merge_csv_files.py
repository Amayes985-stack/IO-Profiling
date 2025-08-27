import os  # Importing the os module for interacting with the file system
import pandas as pd  # Importing pandas for data manipulation and analysis
import sys  # Importing sys to handle command-line arguments

# Function to merge CSV files within a specified directory
def merge_csv_files(directory):
    # Walk through the directory tree starting from the specified directory
    for root, dirs, files in os.walk(directory):
        # Check if the current directory contains performance data (indicated by 'perf' in the path)
        if 'perf' in root:
            # Find all CSV files in the current directory
            csv_files = [os.path.join(root, file) for file in files if file.endswith('.csv')]
            if csv_files:  # If there are any CSV files
                # Load all CSV files into DataFrames and concatenate them into a single DataFrame
                merged_df = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)
                
                # Remove any duplicate rows from the merged DataFrame
                merged_df.drop_duplicates(inplace=True)
                
                # Save the merged DataFrame to a new CSV file called 'data_merged.csv'
                merged_df.to_csv(os.path.join(root, 'data_merged.csv'), index=False)
                
                # Delete the original CSV files after merging
                for file in csv_files:
                    os.remove(file)

# Main script execution starts here
if __name__ == "__main__":
    # The first command-line argument is expected to be the directory to process
    directory_to_move = sys.argv[1]
    
    # Call the function to merge CSV files in the specified directory
    merge_csv_files(directory_to_move)
    
    # Print a message indicating that the CSV files have been merged and filtered
    print("Les fichiers CSV de performance ont été fusionnés et filtrés.")

