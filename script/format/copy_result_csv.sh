#!/bin/bash

# Function to handle errors and exit the script with an error message.
error_exit() {
    echo "Error detected. Reverting changes..."
    exit 1
}

# Check that the script is executed with the correct number of arguments.
if [ "$#" -ne 1 ]; then
    # If not, display the correct usage and exit.
    echo "Usage: $0 <directory_to_process>"
    exit 1
fi

# Set variables for directory paths.
DIRECTORY_TO_PROCESS=$1
LOG_DIR="logs"                            # The main logs directory.
FORMATTED_DIR="${LOG_DIR}/formatted_data" # The directory where formatted data will be stored.
BRUTE_DIR="${LOG_DIR}/brute_data"         # The directory where raw data is stored.

# Function to copy the results.csv file from the brute_data directory to the formatted_data directory.
copy_result_csv() {
    local io_size=$1            # IO block size (e.g., 1s, 128k, 1M).
    local access_pattern=$2      # Access pattern (e.g., RAND, SEQ).
    local file_size=$3           # File size (e.g., 256M, 1G).
    local read_write=$4          # Read/Write mode (READ or WRITE).
    local block_category=$5      # Block size category (small_size_io or big_size_io).

    # Define the source file path and destination directory path.
    local src_file="${BRUTE_DIR}/${DIRECTORY_TO_PROCESS}/${read_write}/${access_pattern}/${block_category}/READ_${io_size}/${file_size}/perf/results.csv"
    local dest_dir="${FORMATTED_DIR}/${DIRECTORY_TO_PROCESS}/${read_write}/${block_category}/${io_size}/${access_pattern}/${file_size}/perf"
    local dest_file="${dest_dir}/results.csv"

    # Check if the source file exists.
    if [ -f "${src_file}" ]; then
        # Create the destination directory if it doesn't exist and copy the file.
        mkdir -p "${dest_dir}" || error_exit
        cp "${src_file}" "${dest_file}" || error_exit
    else
        # If the source file doesn't exist, print a warning message.
        echo "The source file ${src_file} does not exist."
    fi
}

# Iterate through the directories and copy the results.csv files for small block sizes.
for read_write in $(ls "${BRUTE_DIR}/${DIRECTORY_TO_PROCESS}"); do
    for access_pattern in $(ls "${BRUTE_DIR}/${DIRECTORY_TO_PROCESS}/${read_write}"); do
        for size in 1s 128k 16k 512k 8k; do
            for file_size in 256M 1G 4G; do
                copy_result_csv "${size}" "${access_pattern}" "${file_size}" "${read_write}" "small_size_io"
            done
        done
    done
done

# Iterate through the directories and copy the results.csv files for large block sizes.
for read_write in $(ls "${BRUTE_DIR}/${DIRECTORY_TO_PROCESS}"); do
    for access_pattern in $(ls "${BRUTE_DIR}/${DIRECTORY_TO_PROCESS}/${read_write}"); do
        for size in 1M 4M 2M 8M; do
            for file_size in 256M 1G 4G; do
                copy_result_csv "${size}" "${access_pattern}" "${file_size}" "${read_write}" "big_size_io"
            done
        done
    done
done

# Print a message indicating that the results.csv files have been successfully copied.
echo "The results.csv files have been copied."

