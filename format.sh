#!/bin/bash

# Function to handle errors and revert changes (toujours commentée mais corrigée)
#error_exit() {
#    echo "Error detected. Reverting changes..."
#    rm -rf "${FORMATTED_DIR}/${DIRECTORY_TO_MOVE}"
#    mv "${BRUTE_DIR}/${DIRECTORY_TO_MOVE}" "${LOG_DIR}/"
#    rm -rf "${BRUTE_DIR}"
#    exit 1
#}

# Vérification des arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <directory_to_move>"
    exit 1
fi

# Configuration des chemins
DIRECTORY_TO_MOVE=$1
LOG_DIR="logs"
FORMATTED_DIR="${LOG_DIR}/formatted_data"
BRUTE_DIR="${LOG_DIR}/brute_data"
PYTHON_SCRIPT="script/format/wattmeter_format.py"

# Vérification du répertoire logs
if [ ! -d "$LOG_DIR" ]; then
    echo "The directory '$LOG_DIR' does not exist."
    exit 1
fi

# Déplacement sécurisé du répertoire
mkdir -p "${BRUTE_DIR}"
if [ -d "${LOG_DIR}/${DIRECTORY_TO_MOVE}" ]; then
    rsync -a --remove-source-files "${LOG_DIR}/${DIRECTORY_TO_MOVE}/" "${BRUTE_DIR}/${DIRECTORY_TO_MOVE}/"
    rm -rf "${LOG_DIR}/${DIRECTORY_TO_MOVE}"
else
    echo "The directory '${DIRECTORY_TO_MOVE}' does not exist in '${LOG_DIR}'."
    exit 1
fi

# Création du répertoire de destination
DEST_DIR="${FORMATTED_DIR}/${DIRECTORY_TO_MOVE}"
mkdir -p "${DEST_DIR}"

# Fonction de création d'arborescence (syntaxe corrigée)
create_directory_structure() {
    local base_dir=$1
    local access_pattern=$2

    mkdir -p "${base_dir}/small_size_io"
    mkdir -p "${base_dir}/big_size_io"

    for size in 1s 128k 16k 512k 8k; do
        local pattern_dir="${base_dir}/small_size_io/${size}/${access_pattern}"
        mkdir -p "${pattern_dir}"
        create_size_directories "${pattern_dir}"
    done

    for size in 1M 4M 2M 8M; do
        local pattern_dir="${base_dir}/big_size_io/${size}/${access_pattern}"
        mkdir -p "${pattern_dir}"
        create_size_directories "${pattern_dir}"
    done
}

create_size_directories() {
    local pattern_dir=$1
    for file_size in 256M 1G 4G; do
        mkdir -p "${pattern_dir}/${file_size}/energy"
        mkdir -p "${pattern_dir}/${file_size}/perf"
    done
    mkdir -p "${pattern_dir}/baseline"
}

# Fonctions de copie (syntaxe corrigée)
copy_plots() {
    local base_dir=$1
    local access_pattern=$2
    local io_size=$3
    local file_size=$4

    plot_src="${BRUTE_DIR}/${DIRECTORY_TO_MOVE}/READ/${access_pattern}/plot/${io_size}/plot_io_${io_size}_${file_size}.png"
    plot_dest="${base_dir}/${io_size}/${access_pattern}/${file_size}/plot_io_${io_size}_${file_size}.png"

    [ -f "${plot_src}" ] && cp "${plot_src}" "${plot_dest}"

    baseline_src="${BRUTE_DIR}/${DIRECTORY_TO_MOVE}/READ/${access_pattern}/plot/baseline/plot_baseline.png"
    baseline_dest="${base_dir}/${io_size}/${access_pattern}/baseline/plot_baseline.png"
    
    [ -f "${baseline_src}" ] && cp "${baseline_src}" "${baseline_dest}"
}

copy_boxplots() {
    local base_dir=$1
    local access_pattern=$2
    local io_size=$3
    local boxplot_name=$4

    boxplot_src="${BRUTE_DIR}/${DIRECTORY_TO_MOVE}/READ/${access_pattern}/box_plot/${boxplot_name}"
    boxplot_dest="${base_dir}/${io_size}/${access_pattern}/${boxplot_name}"
    
    [ -f "${boxplot_src}" ] && cp "${boxplot_src}" "${boxplot_dest}"
}

copy_baseline_boxplot() {
    local base_dir=$1
    local access_pattern=$2

    boxplot_src="${BRUTE_DIR}/${DIRECTORY_TO_MOVE}/READ/${access_pattern}/box_plot/boxplot_baseline.png"

    if [ -f "${boxplot_src}" ]; then
        for size in 1s 128k 16k 512k 8k; do
            baseline_dest="${base_dir}/small_size_io/${size}/${access_pattern}/baseline/boxplot_baseline.png"
            mkdir -p "$(dirname "${baseline_dest}")"
            cp "${boxplot_src}" "${baseline_dest}"
        done

        for size in 1M 4M 2M 8M; do
            baseline_dest="${base_dir}/big_size_io/${size}/${access_pattern}/baseline/boxplot_baseline.png"
            mkdir -p "$(dirname "${baseline_dest}")"
            cp "${boxplot_src}" "${baseline_dest}"
        done
    fi
}

generate_csv() {
    local json_file=$1
    local csv_file=$2
    python3 "${PYTHON_SCRIPT}" "${json_file}" "${csv_file}"
}

# Correction majeure : syntaxe d'appel des fonctions
format_subdirectories() {
    local current_dir=$1
    for read_write in $(ls "${current_dir}"); do
        for access_pattern in $(ls "${current_dir}/${read_write}"); do
            base_dir="${DEST_DIR}/${read_write}"
            create_directory_structure "${base_dir}" "${access_pattern}"

            # Small size IO
            for size in 1s 128k 16k 512k 8k; do
                for file_size in 256M 1G 4G; do
                    copy_plots "${base_dir}/small_size_io" "${access_pattern}" "${size}" "${file_size}"
                    copy_boxplots "${base_dir}/small_size_io" "${access_pattern}" "${size}" "boxplot_${size}.png"
                    json_src="${current_dir}/${read_write}/${access_pattern}/small_size_io/READ_${size}/READ_${file_size}.json"
                    csv_dest="${base_dir}/small_size_io/${size}/${access_pattern}/${file_size}/energy/data.csv"
                    [ -f "${json_src}" ] && generate_csv "${json_src}" "${csv_dest}"
                done
            done

            # Big size IO
            for size in 1M 4M 2M 8M; do
                for file_size in 256M 1G 4G; do
                    copy_plots "${base_dir}/big_size_io" "${access_pattern}" "${size}" "${file_size}"
                    copy_boxplots "${base_dir}/big_size_io" "${access_pattern}" "${size}" "boxplot_${size}.png"
                    json_src="${current_dir}/${read_write}/${access_pattern}/big_size_io/READ_${size}/READ_${file_size}.json"
                    csv_dest="${base_dir}/big_size_io/${size}/${access_pattern}/${file_size}/energy/data.csv"
                    [ -f "${json_src}" ] && generate_csv "${json_src}" "${csv_dest}"
                done
            done

            copy_baseline_boxplot "${base_dir}" "${access_pattern}"
        done
    done
}

# Exécution principale
format_subdirectories "${BRUTE_DIR}/${DIRECTORY_TO_MOVE}"

# Appel des scripts externes
script/format/generate_perf.sh "${DIRECTORY_TO_MOVE}"
script/format/process_baseline.sh "${DIRECTORY_TO_MOVE}"
script/format/move_perf_files.sh "${DIRECTORY_TO_MOVE}"
script/format/rename_csv_files.sh "${DIRECTORY_TO_MOVE}"
script/format/copy_result_csv.sh "${DIRECTORY_TO_MOVE}"

echo "Operation completed successfully for ${DIRECTORY_TO_MOVE}"
