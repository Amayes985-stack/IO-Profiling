import sys  # Import the sys module to handle command-line arguments
import os  # Import the os module for interacting with the file system
import json  # Import the json module for parsing JSON files
import matplotlib  # Import the matplotlib library for creating plots

matplotlib.use('Agg')  # Use 'Agg' backend for non-interactive environments
import matplotlib.pyplot as plt  # Import pyplot for plotting
from dateutil.parser import parse as parse_date  # Import parse_date for timestamp conversion

# Function to load data from a JSON file
def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Function to read the first and last timestamp from a file
def read_first_and_last_timestamp(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    return lines[0].strip(), lines[-1].strip()

# Function to plot the IO energy data
def plot_io(io_data, io_timestamps, log_dir, sz_bloc, filesize):
    # Convert timestamps and values
    times = [parse_date(d['timestamp']) for d in io_data]
    values = [d['value'] for d in io_data]

    # Create figure with constrained layout for automatic margin handling
    fig, ax = plt.subplots(constrained_layout=True, figsize=(14, 8))

    # Plot watt measurements
    ax.plot(times, values, label=f'Wattmeter during IO - {sz_bloc}', linestyle='-', linewidth=2)

    # Plot vertical lines for IO start/end
    colors = ['green', 'purple']
    for i, (begin, end) in enumerate(io_timestamps):
        ax.axvline(begin, color=colors[i % 2], linestyle='--', linewidth=1, label=f'Start IO {i+1}')
        ax.axvline(end,   color=colors[i % 2], linestyle='--', linewidth=1, label=f'End IO {i+1}')

    # Labels and title
    ax.set_xlabel('Time')
    ax.set_ylabel('Energy (Watts)')
    ax.set_title(f'Energy Consumption - IO size {sz_bloc} & file size {filesize}')

    # Legend inside plot
    ax.legend(loc='best', fontsize='small')

    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    # Grid
    ax.grid(True, which='both', linestyle=':', linewidth=0.5)

    # Save figure
    plot_dir = os.path.join(log_dir, 'plot', sz_bloc)
    os.makedirs(plot_dir, exist_ok=True)
    output = os.path.join(plot_dir, f'plot_io_{sz_bloc}_{filesize}.png')
    fig.savefig(output, bbox_inches='tight')
    plt.close(fig)
    print(f"Plot saved to {output}")

# Main entry
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: python plot_io_all_run_passive.py <log_dir> <sz_bloc>')
        sys.exit(1)

    log_dir, sz_bloc = sys.argv[1], sys.argv[2]
    sizes = ['256M', '1G', '4G']
    for size in sizes:
        small = os.path.join(log_dir, f'small_size_io/READ_{sz_bloc}/READ_{size}.json')
        big   = os.path.join(log_dir, f'big_size_io/READ_{sz_bloc}/READ_{size}.json')
        if os.path.exists(small):
            data_file = small
        elif os.path.exists(big):
            data_file = big
        else:
            print(f"Error: Neither {small} nor {big} exists.")
            continue

        io_data = load_data(data_file)
        ts_dir = os.path.join(log_dir, 'io_timestamp')
        begins = sorted([f for f in os.listdir(ts_dir) if f.startswith(f'io_begin_{sz_bloc}_{size}_iteration_')])
        ends   = sorted([f for f in os.listdir(ts_dir) if f.startswith(f'io_end_{sz_bloc}_{size}_iteration_')])
        if len(begins) != len(ends):
            print(f"Warning: Mismatch in begin/end count for {size}")
            continue
        ts = []
        for b, e in zip(begins, ends):
            bts, _ = read_first_and_last_timestamp(os.path.join(ts_dir, b))
            _, ets = read_first_and_last_timestamp(os.path.join(ts_dir, e))
            ts.append((parse_date(bts), parse_date(ets)))

        plot_io(io_data, ts, log_dir, sz_bloc, size)
