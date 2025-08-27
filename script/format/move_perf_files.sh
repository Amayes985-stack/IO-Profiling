#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory_to_move>"
    exit 1
fi

# Set the directory to be processed
DIRECTORY_TO_MOVE=$1
FORMATTED_DIR="logs/formatted_data/${DIRECTORY_TO_MOVE}"

# Function to move performance files from small_size_io to big_size_io
move_perf_files() {
    # Loop through different combinations of access patterns, read/write modes, block sizes, and file sizes
    for access_pattern in RAND SEQ; do  # Iterate over access patterns: Random (RAND) and Sequential (SEQ)
        for read_write in READ WRITE; do  # Iterate over read/write modes: READ and WRITE
            for size in 1M 2M 4M 8M; do  # Iterate over IO sizes: 1M, 2M, 4M, and 8M
                for file_size in 256M 1G 4G; do  # Iterate over file sizes: 256M, 1G, and 4G

                    # Define the source and destination directories for the performance data
                    local source_dir="${FORMATTED_DIR}/${read_write}/small_size_io/${size}/${access_pattern}/${file_size}/perf"
                    local dest_dir="${FORMATTED_DIR}/${read_write}/big_size_io/${size}/${access_pattern}/${file_size}/perf"

                    # Check if the source directory exists
                    if [ -d "${source_dir}" ]; then
                        # Create the destination directory if it does not exist
                        mkdir -p "${dest_dir}" || exit 1
                        # Move CSV files from the source directory to the destination directory
                        mv "${source_dir}/data"*.csv "${dest_dir}/" || exit 1
                    fi
                done
            done

            # Clean up: Remove the small_size_io directories for the specified sizes
            for size in 1M 2M 4M 8M; do
                rm -rf "${FORMATTED_DIR}/${read_write}/small_size_io/${size}"
            done
        done
    done
}

# Call the function to move the performance files
move_perf_files

# After moving the files, execute a Python script to merge and filter the CSV files
# Determine the path of the current script and the Python script for merging
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/merge_csv_files.py"

# Execute the Python script to merge and filter the performance CSV files
python3 "${PYTHON_SCRIPT}" "${FORMATTED_DIR}"

