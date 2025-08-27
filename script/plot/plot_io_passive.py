import sys  # Import the sys module to handle command-line arguments
import os  # Import the os module for interacting with the file system
import json  # Import the json module for parsing JSON files
import matplotlib  # Import the matplotlib library for creating plots

matplotlib.use('Agg')  # Use 'Agg' backend for non-interactive environments
import matplotlib.pyplot as plt  # Import pyplot for plotting
from dateutil.parser import parse as parse_date  # Parse timestamp strings into datetime objects

# Function to load data from a JSON file
def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Function to read first and last line (timestamp) from a file
def read_first_and_last_timestamp(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    return lines[0].strip(), lines[-1].strip()

# Function to resolve the correct JSON file path, with suffix or without
def find_read_file(log_dir, category, sz_bloc, filesize):
    # Possible filename variants
    variants = [f'READ_{filesize}.json', f'READ_{filesize.rstrip("MG")}.json']
    for name in variants:
        path = os.path.join(log_dir, category, f'READ_{sz_bloc}', name)
        if os.path.exists(path):
            return path
    return None

# Function to create and save the plot
def plot_io(io_data, io_timestamps, log_dir, sz_bloc, filesize):
    times = [parse_date(e['timestamp']) for e in io_data]
    watts = [e['value'] for e in io_data]

    plt.figure(figsize=(12, 8))
    plt.plot(times, watts, label=f'Wattmeter - IO size {sz_bloc}', color='red')

    # Draw start/end markers
    for idx, (start, end) in enumerate(io_timestamps):
        plt.axvline(start, linestyle='--', label=f'Start #{idx+1}')
        plt.axvline(end, linestyle='--', label=f'End #{idx+1}')

    plt.xlabel('Time')
    plt.ylabel('Power (W)')
    plt.title(f'Energy Consump. - IO {sz_bloc}, file {filesize}')
    plt.xticks(rotation=45)
    plt.grid(True)

    # Legends
    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(handles, labels, loc='upper right')

    # Ensure plot directory exists
    out_dir = os.path.join(log_dir, 'plot', sz_bloc)
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f'plot_io_{sz_bloc}_{filesize}.png')
    plt.tight_layout()
    plt.savefig(out_file)
    plt.close()
    print(f"Plot saved: {out_file}")

# Main processing
def main(log_dir, sz_bloc):
    io_sizes = ['256M', '1G', '4G']
    for fs in io_sizes:
        # Determine category and locate JSON
        category_small = 'small_size_io'
        category_big = 'big_size_io'

        read_file = find_read_file(log_dir, category_small, sz_bloc, fs)
        if not read_file:
            read_file = find_read_file(log_dir, category_big, sz_bloc, fs)
        if not read_file:
            print(f"Error: no JSON for size {sz_bloc} / {fs}")
            continue

        # Load measurement data
        data = load_data(read_file)

        # Gather timestamp files
        tdir = os.path.join(log_dir, 'io_timestamp')
        begins = sorted([f for f in os.listdir(tdir) if f.startswith(f'io_begin_{sz_bloc}_{fs}_')])
        ends = sorted([f for f in os.listdir(tdir) if f.startswith(f'io_end_{sz_bloc}_{fs}_')])
        if len(begins) != len(ends):
            print(f"Warning: mismatch begin/end for {sz_bloc} {fs}")
            continue
        io_ts = []
        for b, e in zip(begins, ends):
            b0, _ = read_first_and_last_timestamp(os.path.join(tdir, b))
            _, e1 = read_first_and_last_timestamp(os.path.join(tdir, e))
            io_ts.append((parse_date(b0), parse_date(e1)))

        # Plot
        plot_io(data, io_ts, log_dir, sz_bloc, fs)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python plot_io_passive.py <log_dir> <sz_bloc>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])

