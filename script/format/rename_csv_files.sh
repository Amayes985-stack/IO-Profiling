#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory_to_rename>"
    exit 1
fi

DIRECTORY_TO_RENAME=$1
FORMATTED_DIR="logs/formatted_data/${DIRECTORY_TO_RENAME}"

rename_csv_files() {
    for access_pattern in RAND SEQ; do
        for read_write in READ WRITE; do
            for size in 1M 2M 4M 8M 1s 128k 16k 512k 8k; do
                for file_size in 256M 1G 4G; do
                    for type in energy perf; do
                        # Small size IO
                        base_dir="${FORMATTED_DIR}/${read_write}/small_size_io/${size}/${access_pattern}/${file_size}/${type}"
                        csv_file="${base_dir}/$(if [ "${type}" = "energy" ]; then echo "data.csv"; else echo "data_merged.csv"; fi)"
                        
                        if [ -f "${csv_file}" ]; then
                            new_name="${type}_${access_pattern}_buffer${file_size}_io${size}.csv"
                            mv "${csv_file}" "${base_dir}/${new_name}"
                        fi

                        # Big size IO
                        base_dir="${FORMATTED_DIR}/${read_write}/big_size_io/${size}/${access_pattern}/${file_size}/${type}"
                        csv_file="${base_dir}/$(if [ "${type}" = "energy" ]; then echo "data.csv"; else echo "data_merged.csv"; fi)"
                        
                        if [ -f "${csv_file}" ]; then
                            new_name="${type}_${access_pattern}_buffer${file_size}_io${size}.csv"
                            mv "${csv_file}" "${base_dir}/${new_name}"
                        fi
                    done
                done
            done

            # Gestion baseline
            find "${FORMATTED_DIR}" -type d -name "baseline" | while read -r baseline_dir; do
                baseline_csv="${baseline_dir}/data.csv"
                if [ -f "${baseline_csv}" ]; then
                    mv "${baseline_csv}" "${baseline_dir}/baseline.csv"
                fi
            done
        done
    done
}

rename_csv_files
