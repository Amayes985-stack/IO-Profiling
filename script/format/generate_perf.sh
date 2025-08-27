#!/bin/bash

# Function to handle errors and rollback changes if something goes wrong
error_exit() {
    echo "Erreur détectée. Annulation des modifications..."  # Print an error message
    exit 1  # Exit the script with a status of 1 (indicating an error)
}

# Check if the script is executed with the correct number of arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory_to_process>"  # Print usage information
    exit 1  # Exit the script with a status of 1
fi

# Variables for directories
DIRECTORY_TO_PROCESS=$1
LOG_DIR="logs"
FORMATTED_DIR="${LOG_DIR}/formatted_data"
BRUTE_DIR="${LOG_DIR}/brute_data"

# Path to the Python script responsible for generating performance CSV files
PYTHON_SCRIPT="script/format/generate_perf_csv.py"

# Function to generate performance CSV files
generate_perf_csv() {
    local io_size=$1
    local access_pattern=$2
    local file_size=$3
    local read_write=$4
    local block_category=$5

    iteration=1  # Initialize the iteration counter
    while true; do  # Infinite loop to process multiple iterations
        # Construct the paths to the input JSON files and output CSV file
        io_begin_src="${BRUTE_DIR}/${DIRECTORY_TO_PROCESS}/${read_write}/${access_pattern}/io_timestamp/io_begin_${io_size}_${file_size}_iteration_$(printf "%02d" $iteration).json"
        io_end_src="${BRUTE_DIR}/${DIRECTORY_TO_PROCESS}/${read_write}/${access_pattern}/io_timestamp/io_end_${io_size}_${file_size}_iteration_$(printf "%02d" $iteration).json"
        csv_dest="${FORMATTED_DIR}/${DIRECTORY_TO_PROCESS}/${read_write}/${block_category}/${io_size}/${access_pattern}/${file_size}/perf/data_$(printf "%02d" $iteration).csv"

        # Check if both the begin and end JSON files exist for the current iteration
        if [ -f "${io_begin_src}" ] && [ -f "${io_end_src}" ]; then
            # Create the destination directory if it doesn't exist
            mkdir -p "$(dirname "${csv_dest}")" || error_exit
            # Run the Python script to generate the CSV file
            python3 ${PYTHON_SCRIPT} "${io_begin_src}" "${io_end_src}" "${csv_dest}" "${iteration}" || error_exit
            iteration=$((iteration + 1))  # Increment the iteration counter
        else
            break  # Exit the loop if the files for the current iteration are not found
        fi
    done
}

# Loop through the directories to generate performance CSV files for small block sizes
for read_write in $(ls "${BRUTE_DIR}/${DIRECTORY_TO_PROCESS}"); do
    for access_pattern in $(ls "${BRUTE_DIR}/${DIRECTORY_TO_PROCESS}/${read_write}"); do
        for size in 1s 128k 16k 512k 8k; do
            for file_size in 256M 1G 4G; do
                generate_perf_csv "${size}" "${access_pattern}" "${file_size}" "${read_write}" "small_size_io"
            done
        done
    done
done

# Loop through the directories to generate performance CSV files for large block sizes
for read_write in $(ls "${BRUTE_DIR}/${DIRECTORY_TO_PROCESS}"); do
    for access_pattern in $(ls "${BRUTE_DIR}/${DIRECTORY_TO_PROCESS}/${read_write}"); do
        for size in 1M 4M 2M 8M; do
            for file_size in 256M 1G 4G; do
                generate_perf_csv "${size}" "${access_pattern}" "${file_size}" "${read_write}" "big_size_io"
            done
        done
    done
done

# Print a message indicating that the performance CSV files have been generated
echo "Les fichiers CSV de performance ont été générés."

