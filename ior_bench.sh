#!/bin/bash

# Define file sizes
file_sizes=("256M" "1G" "4G")
# Define I/O size
io_size=512  # 512 bytes
# Define number of blocks (sequential)
nb_bloc=16
# Configurations for Read/Write ratios
configurations=("100:0 , 0:100)
# Storage type and paths
storage_type=$1
path="logs/${storage_type}/IOR"
iterations=1

# Create necessary directories
rm -rf $path
mkdir -p $path
mkdir -p $path/baseline
mkdir -p $path/io_timestamp

for config in "${configurations[@]}"; do
  IFS=":" read read_ratio write_ratio <<< "$config"
  
  for file_size in "${file_sizes[@]}"; do
    echo -e "\033[1;34mRunning IOR with file size: $file_size, I/O size: $io_size bytes, $read_ratio% Read / $write_ratio% Write\033[00m"

    for iter in $(seq 1 $iterations); do
      echo -e "\033[1;34mIteration $iter\033[00m"

      # Log start timestamp before the I/O operations
      starttime=$(date +"%Y-%m-%dT%H:%M:%S.%6N%z")
      echo $starttime > $path/io_timestamp/start_${config}_${file_size}_iter_${iter}.json

      # Write operations
      if [ $write_ratio -gt 0 ]; then
        mpirun -np 1 ./src/ior -a POSIX -b $file_size -t $io_size -w -s $nb_bloc -i $((write_ratio / 100)) -o ior_test_file_${config}_${file_size} -k
        sync  # Ensure the data is fully written to disk
      fi

      # Read operations
      if [ $read_ratio -gt 0 ]; then
        mpirun -np 1 ./src/ior -a POSIX -b $file_size -t $io_size -r -s $nb_bloc -i $((read_ratio / 100)) -o ior_test_file_${config}_${file_size}
      fi

      # Log end timestamp after the I/O operations
      endtime=$(date +"%Y-%m-%dT%H:%M:%S.%6N%z")
      echo $endtime > $path/io_timestamp/end_${config}_${file_size}_iter_${iter}.json

      # Fetch and save energy consumption data
      curl "https://api.grid5000.fr/stable/sites/lyon/metrics?nodes=$(hostname -s)&metrics=wattmetre_power_watt&start_time=$starttime&end_time=$endtime" > $path/${config}_${file_size}_iter_${iter}.json

      # Cleanup: Remove the test file to free up space
      rm -f ior_test_file_${config}_${file_size}

      echo -e "\033[1;33mCompleted iteration $iter for $file_size with $read_ratio% Read and $write_ratio% Write\033[00m"
    done
  done
done

echo -e "\033[1;33mAll tests completed.\033[00m"

