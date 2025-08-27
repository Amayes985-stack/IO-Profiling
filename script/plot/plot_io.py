import sys
import os
import json
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend suitable for scripts
import matplotlib.pyplot as plt
from dateutil.parser import parse as parse_date

def load_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def read_all_timestamps(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    return [line.strip() for line in lines]

def plot_io(io_data, io_timestamps, log_dir, sz_bloc, filesize):
    # Convert timestamps from string to datetime objects for plotting
    io_timestamps_dt = [parse_date(entry['timestamp']) for entry in io_data]
    io_watt_values = [entry['value'] for entry in io_data]

    # Setup the plot with a specific size
    plt.figure(figsize=(12, 8))
    plt.plot(io_timestamps_dt, io_watt_values, label=f'Wattmeter measurements \n during IO - {sz_bloc}', color='red')

    colors = ['green', 'purple']
    for i, (begin, end) in enumerate(io_timestamps):
        color = colors[i % 2]
        plt.axvline(x=begin, color=color, linestyle='dashed', linewidth=1, label=f'Début IO {i+1}')
        plt.axvline(x=end, color=color, linestyle='dashed', linewidth=1, label=f'Fin IO {i+1}')

    plt.xlabel('Time')
    plt.ylabel('Energy Consumption (Watts)')
    plt.title(f'Energy Consumption over Time - IO size {sz_bloc} & buffer size {filesize}')
    
    # Création manuelle de la légende
    handles, labels = plt.gca().get_legend_handles_labels()
    
    # Légende pour la 1ère ligne (corrigé)
    legend1 = plt.legend(handles[:1], labels[:1], loc='upper right', bbox_to_anchor = (1.005, 1),
           bbox_transform = plt.gcf().transFigure)
    plt.gca().add_artist(legend1)  # Ajout de la 1ère légende au graphique

    # Légende pour les autres lignes
    legend2 = plt.legend(handles[1:], labels[1:], loc='upper right', ncol=1, bbox_to_anchor = (1.005, 0.95),
           bbox_transform = plt.gcf().transFigure)

    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Create the plot directory if it doesn't exist
    plot_dir = os.path.join(log_dir, 'plot', sz_bloc)
    os.makedirs(plot_dir, exist_ok=True)

    output_path = os.path.join(plot_dir, f'plot_io_{sz_bloc}_{filesize}_all_run.png')
    plt.savefig(output_path)
    plt.show()

    print(f"Plot saved to {output_path}")

def main(log_dir, sz_bloc):
    io_sizes = ['256M', '1G', '4G']
    for filesize in io_sizes:
        read_file_small = os.path.join(log_dir, f'small_size_io/READ_{sz_bloc}/READ_{filesize}.json')
        read_file_big = os.path.join(log_dir, f'big_size_io/READ_{sz_bloc}/READ_{filesize}.json')
        
        if os.path.exists(read_file_small):
            read_file = read_file_small
        elif os.path.exists(read_file_big):
            read_file = read_file_big
        else:
            print(f"Error: Neither {read_file_small} nor {read_file_big} exists.")
            continue

        io_data = load_data(read_file)

        # Lister tous les fichiers io_begin et io_end disponibles
        timestamp_dir = os.path.join(log_dir, 'io_timestamp')
        io_begin_files = sorted([f for f in os.listdir(timestamp_dir) if f.startswith(f'io_begin_{sz_bloc}_{filesize}_iteration_')])
        io_end_files = sorted([f for f in os.listdir(timestamp_dir) if f.startswith(f'io_end_{sz_bloc}_{filesize}_iteration_')])

        if len(io_begin_files) != len(io_end_files):
            print(f"Warning: Mismatch in number of begin and end files for size {filesize}")
            continue

        # Lire les timestamps
        begin_timestamps = [read_all_timestamps(os.path.join(timestamp_dir, f)) for f in io_begin_files]
        end_timestamps = [read_all_timestamps(os.path.join(timestamp_dir, f)) for f in io_end_files]

        # Flatten the lists of lists
        begin_timestamps = [ts for sublist in begin_timestamps for ts in sublist]
        end_timestamps = [ts for sublist in end_timestamps for ts in sublist]

        if len(begin_timestamps) != len(end_timestamps):
            print(f"Warning: Mismatch in number of begin and end timestamps for size {filesize}")
            continue

        io_timestamps = list(zip(begin_timestamps, end_timestamps))

        # Convertir les timestamps en objets datetime
        io_timestamps = [(parse_date(begin), parse_date(end)) for begin, end in io_timestamps]

        plot_io(io_data, io_timestamps, log_dir, sz_bloc, filesize)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python plot_io.py <log_dir> <sz_bloc>")
        sys.exit(1)
    log_dir = sys.argv[1]
    sz_bloc = sys.argv[2]
    main(log_dir, sz_bloc)

