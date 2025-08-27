import sys
import matplotlib.pyplot as plt
import numpy as np

def read_normalized_offsets(filename):
    """
    Read a file containing normalized offsets (one per line)
    and return them as a list of floating-point numbers.

    Args:
        filename (str): Path to the data file.

    Returns:
        list: A list of normalized offset values (floats).
    """
    normalized_offsets = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                try:
                    # Convert each line into a float and store it
                    normalized_offsets.append(float(line.strip()))
                except ValueError:
                    # Ignore malformed lines and print a warning
                    print(f"Warning: Skipping line due to invalid format: '{line.strip()}'", file=sys.stderr)
    except FileNotFoundError:
        # Handle case where the file does not exist
        print(f"Error: The file '{filename}' was not found.", file=sys.stderr)
        return None
    except Exception as e:
        # Catch any other unexpected errors during file reading
        print(f"An error occurred while reading the file: {e}", file=sys.stderr)
        return None
    return normalized_offsets

def plot_horizontal_distribution(data, title):
    """
    Plot a horizontal bar chart to visualize the distribution of normalized offsets,
    including mean and key percentiles.

    Args:
        data (list): List of normalized offsets to plot.
        title (str): Title of the plot.
    """
    if not data:
        print("The data list is empty. No plot or calculations can be performed.")
        return
    
    np_data = np.array(data)

    # Compute descriptive statistics
    mean_val = np.mean(np_data)
    p25 = np.percentile(np_data, 25)   # 25th percentile (Q1)
    p50 = np.percentile(np_data, 50)   # 50th percentile (Median)
    p75 = np.percentile(np_data, 75)   # 75th percentile (Q3)
    p90 = np.percentile(np_data, 90)   # 90th percentile

    # Print statistics in the terminal
    print("--- Statistics of Normalized Offsets ---")
    print(f"Mean: {mean_val:.4f}")
    print(f"25th percentile (Q1): {p25:.4f}")
    print(f"50th percentile (Median): {p50:.4f}")
    print(f"75th percentile (Q3): {p75:.4f}")
    print(f"90th percentile: {p90:.4f}")
    print("---------------------------------------")

    # Create a figure
    plt.figure(figsize=(12, 8))
    
    # Build histogram to compute frequencies and bin ranges
    n_bins = 20
    counts, bin_edges = np.histogram(np_data, bins=n_bins)
    
    # Plot horizontal bar chart
    # bin_edges[:-1] gives the starting position of each bar
    plt.barh(bin_edges[:-1], counts, height=(bin_edges[1] - bin_edges[0]) * 0.8,
             color='skyblue', edgecolor='black', alpha=0.7)
    
    # Add horizontal lines for statistical markers
    plt.axhline(mean_val, color='darkorange', linestyle='-', linewidth=2, label=f'Mean ({mean_val:.4f})')
    plt.axhline(p50, color='red', linestyle='--', linewidth=2, label=f'Median ({p50:.4f})')
    plt.axhline(p25, color='green', linestyle='--', linewidth=1, label=f'25th percentile ({p25:.4f})')
    plt.axhline(p75, color='purple', linestyle='--', linewidth=1, label=f'75th percentile ({p75:.4f})')
    
    # Add labels, title, legend, and grid
    plt.title(title, fontsize=18, fontweight='bold')
    plt.xlabel("Frequency (number of requests)", fontsize=14)
    plt.ylabel("Normalized Offset Value", fontsize=14)
    plt.legend(loc='upper right', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    file_path = "ter_normal_r_ior.txt"  # Make sure this file exists
    
    # Read normalized offsets from file
    offsets_data = read_normalized_offsets(file_path)

    # Plot distribution if data is available
    if offsets_data:
        plot_horizontal_distribution(offsets_data, "Frequency Distribution of Normalized Offsets (Horizontal)")

