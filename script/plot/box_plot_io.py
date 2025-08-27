import os
import sys
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Usage: python box_plot_io.py <log_dir> <sz_bloc>
if len(sys.argv) != 3:
    print("Usage: python box_plot_io.py <log_dir> <sz_bloc>")
    sys.exit(1)

log_dir = sys.argv[1]
sz_bloc = sys.argv[2]

# File sizes for which to generate boxplots
io_sizes = ['256M', '1G', '4G']

for size in io_sizes:
    # Path for small and big IO JSON files under the block-size directory
    small_json = os.path.join(log_dir, 'small_size_io', f'READ_{sz_bloc}', f'READ_{size}.json')
    big_json   = os.path.join(log_dir, 'big_size_io',   f'READ_{sz_bloc}', f'READ_{size}.json')

    if os.path.exists(small_json):
        json_file = small_json
    elif os.path.exists(big_json):
        json_file = big_json
    else:
        print(f"Error: Neither {small_json} nor {big_json} exists.")
        continue

    # Load and normalize JSON data
    with open(json_file, 'r') as f:
        data = json.load(f)
    df = pd.json_normalize(data)
    df = df[df['metric_id'] == 'wattmetre_power_watt'].copy()
    df['label'] = f'{sz_bloc}_{size}'

    # Plot boxplot without constrained_layout to avoid conflicts
    fig, ax = plt.subplots(figsize=(10, 6))
    box = df.boxplot(column='value', by='label', ax=ax,
                     grid=True, showfliers=False, patch_artist=True)

    # Style the box elements
    for patch in box.artists:
        patch.set_facecolor('purple')
        patch.set_edgecolor('black')

    # Set titles and labels
    ax.set_title(f'Boxplot Wattmeter during IO - Block {sz_bloc}, File {size}')
    ax.set_xlabel('')
    ax.set_ylabel('Watts')
    plt.suptitle('')
    plt.xticks(rotation=45, ha='right')
    ax.grid(True, linestyle='--', linewidth=0.7, alpha=0.7)

    # Adjust layout to prevent clipping of labels
    fig.tight_layout()

    # Ensure output directory exists per block-size
    out_dir = os.path.join(log_dir, 'box_plot', sz_bloc)
    os.makedirs(out_dir, exist_ok=True)
    output_path = os.path.join(out_dir, f'box_{sz_bloc}_{size}.png')
    fig.savefig(output_path)
    plt.close(fig)

    print(f"Boxplot saved to {output_path}")

