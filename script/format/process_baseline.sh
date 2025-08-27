#!/bin/bash

# Function to handle errors and clean up if needed
error_exit() {
    echo "Error detected. Rolling back changes..."
    rm -f "$output_csv_file"  # Remove the CSV file if something goes wrong
    exit 1
}

# Path to the Python script that formats the baseline data
PYTHON_SCRIPT="script/format/format_baseline.py"

# Path to the baseline.json file in the brute_data directory
baseline_json="logs/brute_data/$1/READ/RAND/baseline/baseline.json"

# Check if the baseline.json file exists
if [ ! -f "$baseline_json" ]; then
    echo "The file baseline.json does not exist in $baseline_json."
    exit 1
fi

# List of directories where the formatted CSV file should be placed
directories=(
    # Small IO size, random access, read mode
    "logs/formatted_data/$1/READ/small_size_io/1s/RAND/baseline"
    "logs/formatted_data/$1/READ/small_size_io/128k/RAND/baseline"
    "logs/formatted_data/$1/READ/small_size_io/16k/RAND/baseline"
    "logs/formatted_data/$1/READ/small_size_io/512k/RAND/baseline"
    "logs/formatted_data/$1/READ/small_size_io/8k/RAND/baseline"
    # Big IO size, random access, read mode
    "logs/formatted_data/$1/READ/big_size_io/1M/RAND/baseline"
    "logs/formatted_data/$1/READ/big_size_io/4M/RAND/baseline"
    "logs/formatted_data/$1/READ/big_size_io/2M/RAND/baseline"
    "logs/formatted_data/$1/READ/big_size_io/8M/RAND/baseline"
    # Small IO size, sequential access, read mode
    "logs/formatted_data/$1/READ/small_size_io/1s/SEQ/baseline"
    "logs/formatted_data/$1/READ/small_size_io/128k/SEQ/baseline"
    "logs/formatted_data/$1/READ/small_size_io/16k/SEQ/baseline"
    "logs/formatted_data/$1/READ/small_size_io/512k/SEQ/baseline"
    "logs/formatted_data/$1/READ/small_size_io/8k/SEQ/baseline"
    # Big IO size, sequential access, read mode
    "logs/formatted_data/$1/READ/big_size_io/1M/SEQ/baseline"
    "logs/formatted_data/$1/READ/big_size_io/4M/SEQ/baseline"
    "logs/formatted_data/$1/READ/big_size_io/2M/SEQ/baseline"
    "logs/formatted_data/$1/READ/big_size_io/8M/SEQ/baseline"
    # Small IO size, random access, write mode
    "logs/formatted_data/$1/WRITE/small_size_io/1s/RAND/baseline"
    "logs/formatted_data/$1/WRITE/small_size_io/128k/RAND/baseline"
    "logs/formatted_data/$1/WRITE/small_size_io/16k/RAND/baseline"
    "logs/formatted_data/$1/WRITE/small_size_io/512k/RAND/baseline"
    "logs/formatted_data/$1/WRITE/small_size_io/8k/RAND/baseline"
    # Big IO size, random access, write mode
    "logs/formatted_data/$1/WRITE/big_size_io/1M/RAND/baseline"
    "logs/formatted_data/$1/WRITE/big_size_io/4M/RAND/baseline"
    "logs/formatted_data/$1/WRITE/big_size_io/2M/RAND/baseline"
    "logs/formatted_data/$1/WRITE/big_size_io/8M/RAND/baseline"
    # Small IO size, sequential access, write mode
    "logs/formatted_data/$1/WRITE/small_size_io/1s/SEQ/baseline"
    "logs/formatted_data/$1/WRITE/small_size_io/128k/SEQ/baseline"
    "logs/formatted_data/$1/WRITE/small_size_io/16k/SEQ/baseline"
    "logs/formatted_data/$1/WRITE/small_size_io/512k/SEQ/baseline"
    "logs/formatted_data/$1/WRITE/small_size_io/8k/SEQ/baseline"
    # Big IO size, sequential access, write mode
    "logs/formatted_data/$1/WRITE/big_size_io/1M/SEQ/baseline"
    "logs/formatted_data/$1/WRITE/big_size_io/4M/SEQ/baseline"
    "logs/formatted_data/$1/WRITE/big_size_io/2M/SEQ/baseline"
    "logs/formatted_data/$1/WRITE/big_size_io/8M/SEQ/baseline"
)

# Loop through each directory, create it, and place the formatted CSV file in it
for dir in "${directories[@]}"; do
    mkdir -p "$dir" || error_exit  # Create the directory if it doesn't exist
    output_csv_file="${dir}/data.csv"  # Define the path for the output CSV file
    # Run the Python script to format the baseline.json and generate the CSV
    python3 "$PYTHON_SCRIPT" "$baseline_json" "$output_csv_file" || error_exit
done

echo "The baseline.json file has been formatted and placed in the appropriate directories."

