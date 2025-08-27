#!/bin/bash

# Compile the IO's program
# This command compiles the C program iotest.c, which is responsible for performing the actual IO operations.
gcc -g iotest.c -lm

######## OPTIONS

# Define maximum repetitions for small and big block sizes
MAX_REP_SMALL=100   # Number of repetitions for small block sizes
MAX_REP_BIG=100     # Number of repetitions for big block sizes
MAX_REP=10          # General number of repetitions for unspecified cases

# Capture mode (read/write), access pattern (sequential/random), and storage type (HDD/SSD) from command-line arguments
mode=$1
access_pattern=$2
storage_type=$3

# Define the number of blocks to be read or written based on the access pattern
if [ "$access_pattern" == "SEQ" ]; then
    nb_bloc=16           # Sequential access will use 16 blocks
    access_type="SEQ"    # Label the access type as SEQ (sequential)
else
    nb_bloc=1            # Random access will use 1 block
    access_type="RAND"   # Label the access type as RAND (random)
fi

# Define block sizes for small and big blocks
small_blocks=("1s" "8k" "16k" "128k" "512k")  # Block sizes for small IO operations
big_blocks=("1M" "2M" "4M" "8M")              # Block sizes for big IO operations

# Define the path to store logs based on storage type, mode, and access pattern
path="logs/${storage_type}/${mode}/${access_pattern}"

# Base options for running the IO program with small and big blocks
base_option_small="--mode ${mode,,} --nb_run $MAX_REP_SMALL --nb_bloc $nb_bloc --skip 0"
base_option_big="--mode ${mode,,} --nb_run $MAX_REP_BIG --nb_bloc $nb_bloc --skip 0"

######## 

# Create necessary directories and avoid duplicates
# Remove any existing directory at the specified path
rm -rf $path

# Create fresh directories for logs, baseline, and IO timestamps
mkdir -p logs
mkdir -p $path
mkdir -p $path/baseline
mkdir -p $path/io_timestamp

# Create directories for each block size within the path
for sz_bloc in "${small_blocks[@]}" "${big_blocks[@]}"
do
    mkdir -p $path/{small_size_io,big_size_io}/READ_${sz_bloc}
done

## Measure baseline energy consumption without IO operations for 15 minutes

echo -e "\033[1;33mMesure énergie à vide... 15 minutes\033[00m"

# Record start time
starttime=$(date +%s.%6N)

# Sleep for 900 seconds (15 minutes)
sleep 900

# Record end time
endtime=$(date +%s.%6N)

# Fetch energy consumption data from the Grid5000 API for the recorded time period and save it in a JSON file
curl "https://api.grid5000.fr/stable/sites/lyon/metrics?nodes=$(hostname -s)&metrics=wattmetre_power_watt&start_time=$starttime&end_time=$endtime" > $path/baseline/baseline.json

# Perform a dry run to validate the parameters by running the compiled program without actual IO operations
sudo-g5k ./a.out $base_option_small --dry

# Print the mode, path, and hostname for reference
echo "$mode -- $path -- $(hostname -s)"

# ------- Begin IO Operations for Small Blocks -------- #
for sz_bloc in "${small_blocks[@]}"
do
    block_category="small_size_io"
    for filesize in 256M 1G 4G  # Iterate through different file sizes (small, medium, large)
    do
        # Set options for small block sizes
        option="$base_option_small --sz_bloc $sz_bloc --filesize $filesize"
        SECONDS=0  # Reset the timer

        echo -e "\033[1;34mfilesize: $filesize -- sz_bloc: $sz_bloc\033[00m"

        # Record start time
        starttime=$(date +%s.%6N)

        # Perform IO operations multiple times (MAX_REP_SMALL)
        for rep in `seq -f "%02g" 1 $MAX_REP`
        do
            # Run the IO operation and save the result
            result=$(sudo-g5k ./a.out $option | tee /dev/tty)
            
            # Create directory for storing performance results
            perf_dir="$path/${block_category}/READ_${sz_bloc}/${filesize}/perf"
            mkdir -p "$perf_dir"

            # Save the result in a CSV file
            echo "$result" >> "$perf_dir/results.csv"

            # Move the start and end timestamp logs to the appropriate directory
            mv log_epoch_start.txt $path/io_timestamp/io_begin_${sz_bloc}_${filesize}_iteration_${rep}.json
            mv log_epoch_end.txt $path/io_timestamp/io_end_${sz_bloc}_${filesize}_iteration_${rep}.json

            # Pause for 90 seconds before the next iteration
            sleep 90
        done

        # Record end time
        endtime=$(date +%s.%6N)

        # Fetch energy consumption data from the Grid5000 API for the recorded time period and save it in a JSON file (change 'lyon' by the site you will use (do that for every curl request)
        curl "https://api.grid5000.fr/stable/sites/lyon/metrics?nodes=$(hostname -s)&metrics=wattmetre_power_watt&start_time=$starttime&end_time=$endtime" > $path/${block_category}/READ_${sz_bloc}/READ_${filesize}.json
    done
done

# ------- Begin IO Operations for Big Blocks -------- #
for sz_bloc in "${big_blocks[@]}"
do
    block_category="big_size_io"
    for filesize in 256M 1G 4G  # Iterate through different file sizes (small, medium, large)
    do
        # Set options for big block sizes
        option="$base_option_big --sz_bloc $sz_bloc --filesize $filesize"
        SECONDS=0  # Reset the timer

        echo -e "\033[1;34mfilesize: $filesize -- sz_bloc: $sz_bloc\033[00m"

        # Record start time
        starttime=$(date +%s.%6N)

        # Perform IO operations multiple times (MAX_REP_BIG)
        for rep in `seq -f "%02g" 1 $MAX_REP`
        do
            # Run the IO operation and save the result
            result=$(sudo-g5k ./a.out $option | tee /dev/tty)
            
            # Create directory for storing performance results
            perf_dir="$path/${block_category}/READ_${sz_bloc}/${filesize}/perf"
            mkdir -p "$perf_dir"

            # Save the result in a CSV file
            echo "$result" >> "$perf_dir/results.csv"

            # Move the start and end timestamp logs to the appropriate directory
            mv log_epoch_start.txt $path/io_timestamp/io_begin_${sz_bloc}_${filesize}_iteration_${rep}.json
            mv log_epoch_end.txt $path/io_timestamp/io_end_${sz_bloc}_${filesize}_iteration_${rep}.json

            # Pause for 90 seconds before the next iteration
            sleep 90
        done

        # Record end time
        endtime=$(date +%s.%6N)

        # Fetch energy consumption data from the Grid5000 API for the recorded time period and save it in a JSON file
        curl "https://api.grid5000.fr/stable/sites/lyon/metrics?nodes=$(hostname -s)&metrics=wattmetre_power_watt&start_time=$starttime&end_time=$endtime" > $path/${block_category}/READ_${sz_bloc}/READ_${filesize}.json
    done
done

# Clean up unnecessary directories
# Remove directories that do not match the current block size categories
rm -r $path/big_size_io/READ_1s/ $path/big_size_io/READ_16k/ $path/big_size_io/READ_8k/ $path/big_size_io/READ_512k/ $path/big_size_io/READ_128k/
rm -r $path/small_size_io/READ_1M/ $path/small_size_io/READ_2M/ $path/small_size_io/READ_4M/ $path/small_size_io/READ_8M/

# Print a completion message
echo -e "\033[1;33mDone.. Exit\033[00m"

