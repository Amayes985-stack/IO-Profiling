import sys

def normalize_offsets(offsets):
    """
    Normalize a list of numerical values using the Min-Max method.

    The normalization formula is: (x - min_val) / (max_val - min_val)

    Args:
        offsets (list): A list of offsets (integers or floats) to normalize.

    Returns:
        list: A new list of normalized offsets (values between 0.0 and 1.0).
    """
    if not offsets:
        return []

    # Find the minimum and maximum values in the offsets list
    min_val = min(offsets)
    max_val = max(offsets)

    # Handle the case where all values are identical (avoid division by zero)
    if max_val == min_val:
        return [0.0] * len(offsets)

    # Apply Min-Max normalization formula to each offset
    normalized_offsets = [(offset - min_val) / (max_val - min_val) for offset in offsets]
    
    return normalized_offsets

def read_offsets_from_file(filename):
    """
    Read a trace file, extract the second column (offsets),
    and return them as a list of integers.

    Args:
        filename (str): Path to the trace file.

    Returns:
        list: A list of extracted offsets (integers).
    """
    offsets = []
    try:
        with open(filename, 'r') as file:
            for line in file:
                # Split the line into words and ensure there are at least two columns
                parts = line.split()
                if len(parts) > 1:
                    try:
                        # Convert the second column to integer and add it to the list
                        offsets.append(int(parts[1]))
                    except (ValueError, IndexError):
                        # Skip malformed lines and log a warning to stderr
                        print(f"Warning: Skipping line '{line.strip()}' due to incorrect format.", file=sys.stderr)
    except FileNotFoundError:
        # Handle case where the input file does not exist
        print(f"Error: The file '{filename}' was not found.", file=sys.stderr)
        return None
    except Exception as e:
        # Catch any other unexpected errors during file reading
        print(f"An error occurred while reading the file: {e}", file=sys.stderr)
        return None
    return offsets

if __name__ == "__main__":
    file_path = "trace.txt"  # Make sure this filename is correct and exists
    
    # Read offsets from the file
    input_offsets = read_offsets_from_file(file_path)

    if input_offsets:
        # Normalize the list using Min-Max normalization
        normalized_list = normalize_offsets(input_offsets)

        # Print normalized offsets
        print("List of normalized offsets (Min-Max):")
        for offset in normalized_list:
            # Display with 6 decimal places for better readability
            print(f"{offset:.6f}")

