# IO-Profiling : Energy Consumption Analysis for IO Operations

Welcome to the repository for my internship project focused on the analysis of energy consumption during input/output (IO) operations. This project includes a set of scripts and tools designed to calculate, visualize, and compare energy consumption using different methods. The main goal is to determine the most accurate approach for measuring energy consumed by IO operations, specifically focusing on projections and averages.

-----

## Table of Contents

1.  [Project Overview](#project-overview)
2.  [Project Structure](#project-structure)
3.  [Installation](https://www.google.com/search?q=%23installation)
4.  [Usage](https://www.google.com/search?q=%23usage)
      - [Example: Compiling and Running `iotest.c`](https://www.google.com/search?q=%23example-compiling-and-running-iotestc)
      - [Running the `iotest` Benchmark](https://www.google.com/search?q=%23running-the-iotest-benchmark)
      - [Running the `ior_bench.sh` Benchmark](https://www.google.com/search?q=%23running-the-ior_benchsh-benchmark)
      - [Plotting Results](https://www.google.com/search?q=%23plotting-results)
5.  [Scripts Explanation](https://www.google.com/search?q=%23scripts-explanation)
      - [iotest.c and iotest.h](https://www.google.com/search?q=%23iotestc-and-iotesth)
      - [benchmark.sh](https://www.google.com/search?q=%23benchmarksh)
      - [ior\_bench.sh](https://www.google.com/search?q=%23iorbench)
      - [plotting.sh](https://www.google.com/search?q=%23plottingsh)
      - [format.sh](https://www.google.com/search?q=%23formatsh)
      - [New Scripts and Tools](https://www.google.com/search?q=%23new-scripts-and-tools)
6.  [Guide to Installing and Using IOR for I/O Performance Analysis](https://www.google.com/search?q=%23guide-to-installing-and-using-ior-for-io-performance-analysis)
      - [1. Environment Setup](https://www.google.com/search?q=%231-environment-setup)
      - [2. Installing Dependencies](https://www.google.com/search?q=%232-installing-dependencies)
      - [3. Installing IOR](https://www.google.com/search?q=%233-installing-ior)
      - [4. Running IOR Benchmarks](https://www.google.com/search?q=%234-running-ior-benchmarks)
      - [5. Capturing an I/O Trace with strace](https://www.google.com/search?q=%235-capturing-an-io-trace-with-strace)
      - [6. Filtering and Formatting the Trace](https://www.google.com/search?q=%236-filtering-and-formatting-the-trace)
      - [7. Replaying the Captured Trace](https://www.google.com/search?q=%237-replaying-the-captured-trace)

-----

## Project Overview

This project was developed during my internship and aims to analyze energy consumption during IO operations on storage devices. The focus is on calculating the exact energy consumed using wattmeter readings and comparing these calculations using different methods such as projection and average energy methods. The scripts automate the entire process from data collection to analysis and visualization.

-----

## Project Structure

The project is organized as follows:

```plaintext
├── benchmark.sh            # Script for running IO benchmarks
├── format.sh               # Script for formatting and processing raw data
├── plotting.sh             # Script for plotting raw data
├── logs/                   # Directory containing raw and processed data files
├── scripts/                # Directory containing all Python and Shell scripts
│   ├── plot/               # Directory containing scripts for plotting
│        └── ...
│   ├── format/             # Directory containing scripts for formatting
│        └── ...
│   ├── math/               # Directory containing scripts for mathematical computations
│        └── normalize.py    # Script to calculate normalized offsets
│        └── frequency.py    # Script to display frequency distributions
│        └── ...             
│   └── IOR/                # Directory containing IOR-related tools
│        └── iortest1.c    # C program based on iotest with IOR trace functionality
│        └── filter_traces.c # C program for filtering IOR traces
├── README.md       
```

-----

## Usage

### Example: Compiling and Running `iotest.c`

The `iotest.c` file is a C program used to simulate IO operations. The associated header file, `iotest.h`, contains the definitions and functions used within the `iotest.c` file.

#### Compiling `iotest.c`

To compile the `iotest.c` program, use the following command:

```bash
gcc -g iotest.c -o iotest -lm
```

This command compiles the C code and creates an executable named `iotest`.

### Running the `iotest` Benchmark

The `benchmark.sh` script is used to run IO operations and measure energy consumption. Here's an example of how to run the benchmark:

```bash
sudo-g5k ./benchmark.sh READ RAND HDD
```

This script runs the IO benchmark with specified parameters (READ or WRITE mode, RANDOM or SEQUENTIAL (RAND or SEQ) access pattern, HDD or SSD storage type) and stores the results in the `logs/` directory.

### Running the `ior_bench.sh` Benchmark

The `ior_bench.sh` script is a specialized benchmark for measuring energy consumption using `iortest1.c`. It's designed to test different read/write ratios and file sizes, and it captures energy data directly via the Grid5000 API.

#### Execution Command

This script takes one argument: the storage type (`HDD` or `SSD`).

```bash
./ior_bench.sh <storage_type>
```

For example, to run the benchmark on an HDD:

```bash
./ior_bench.sh HDD
```

### Plotting Script (plotting.sh)

The `plotting.sh` script is used to generate various plots from the benchmark results. It supports different types of plots, such as baseline plots, boxplots, and IO energy consumption plots.

#### Usage Example:

```bash
./plotting.sh <log_dir> <type> [<optional_arg>]
```

  - `log_dir`: The directory containing log files at the base of the logs (see example below).
  - `type`: The type of plot to generate (e.g., `baseline` or `sz_bloc)`.
  - `optional_arg`: An optional argument to specify additional options (e.g., `nb_run`).

For example, to generate ALL plot for all runs per iteration:

```bash
./plotting.sh logs/HDD/READ/RAND/ plot_all nb_run
```

-----

## Scripts Explanation

### iotest.c and iotest.h

  - `iotest.c`: This C program simulates IO operations by reading and writing data to a storage device. It is highly configurable with various command-line options that allow you to specify the mode (READ/WRITE), the number of iterations, block sizes, and file sizes.

  - `iotest.h`: The header file contains function prototypes, macros, and structure definitions used in `iotest.c`. It helps in organizing the code and making the functions available across different files.

### benchmark.sh

  - `benchmark.sh`: This shell script automates the process of running IO benchmarks on different storage devices. It compiles the `iotest.c` program, defines block sizes and file sizes, and runs multiple iterations of the IO operations while capturing the energy consumption data from a wattmeter. The results are stored in structured directories for later analysis.

### ior\_bench.sh

  - `ior_bench.sh`: This shell script automates the process of running IO benchmarks on different storage devices using the **IOR library**. It defines file sizes and I/O ratios to test mixed read/write workloads. The script runs each configuration, captures energy consumption data from a wattmeter using the Grid5000 API, and stores the results in structured directories for later analysis.

### plotting.sh

  - `plotting.sh`: This shell script is designed to generate visual plots of the energy consumption data collected during the benchmarks. It can produce different types of plots depending on the provided arguments. The script calls various Python scripts to generate baseline plots, boxplots, and IO-specific plots.

### format.sh

The `format.sh` script is used to organize and format raw data collected during IO tests by structuring it into a more manageable format for subsequent analysis and visualization.

#### Usage

```bash
./format.sh <directory_to_move>
```

  - `<directory_to_move>`: The name of the directory containing the raw data to be formatted. This directory will be moved into the `logs/brute_data` folder, in our case it will be either `SSD` or `HDD` (contained in `logs/`).

#### Main Features

  - **Moving Raw Data**: The script moves the specified directory containing raw data into `logs/brute_data`.
  - **Creating Formatted Directory Structure**: A new directory structure is created in `logs/formatted_data` to organize data by block size and access type (sequential or random).
  - **Formatting Energy Data**: JSON files containing energy measurements are converted to CSV files. The CSV files are then placed in the appropriate directories.
  - **Copying Plots**: Generated plots and boxplots are copied into the corresponding directories under `formatted_data`.
  - **Executing Additional Formatting Scripts**:
      - `generate_perf.sh`: Generates performance CSV files using another python script (same name).
      - `process_baseline.sh`: Formats baseline data using another python script.
      - `move_perf_files.sh`: Moves and merges performance CSV files.
      - `merge_csv_files.py`: Merges all the perf CSV files (each of them corresponds to each iteration).
      - `rename_csv_files.sh`: Renames CSV files for clear organization.
      - `move_perf_files.sh`: Moves the perf and energy files into the correct directories.

#### Example

To format raw data from the HDD benchmarking in the `logs/` directory:

```bash
./format.sh HDD
```

After running the script, the `HDD` directory will be moved to `logs/brute_data`, and the formatted data will be available in `logs/formatted_data/HDD`.

-----

### New Scripts and Tools

In the `scripts/` directory, new tools have been added to enhance analysis capabilities:

#### `scripts/IOR/`

  - **`iortest1.c`**: This is a modified version of `iotest.c` that includes functionality to trace IOR operations. This program combines the simulation of IO operations with the ability to capture their trace, which is crucial for detailed performance and energy analysis.
  - **`filter_traces.c`**: This C program is designed to parse the raw trace data generated by `iortest1.c` (or other tracing tools like `strace`). It extracts relevant information (operation type, offset, and size) and formats it into a clean, structured file, making the trace data usable for subsequent analysis and replay.

#### `scripts/math/`

  - **`normalize.py`**: A Python script to calculate **normalized offsets** for IO operations. Normalization helps in comparing the spatial distribution of IO requests across different test runs, providing insights into access patterns independent of the absolute file size.
  - **`frequency.py`**: This script is used to display the **frequency distribution** of IO requests. It visualizes how often certain types of requests or requests at specific offsets occur, which is a powerful way to understand the workload's characteristics.

-----

## Guide to Installing and Using IOR for I/O Performance Analysis

This document describes the complete process for installing the IOR I/O benchmark, running it to measure performance, capturing a trace of its operations with `strace`, filtering that trace, and finally replaying it with a custom tool.

### 1\. Environment Setup

All operations are performed on a compute cluster using the OAR resource manager.

#### Node Reservation

An interactive reservation is made for a single node with an allocated time of 7 hours.

```bash
oarsub -I -l host=1,walltime=7:00 -q default -p taurus -t deploy
```

#### Operating System Deployment

A Debian 11 environment is deployed on the reserved node.

```bash
kadeploy3 debian11-big
```

### 2\. Installing Dependencies

Once on the node, the necessary packages for compiling and running IOR are installed.

```bash
# Update the package list
apt-get update

# Basic compilation tools and MPI
apt-get install -y build-essential openmpi-bin

# Libraries for I/O backends (HDF5, NetCDF, PnetCDF)
apt-get install -y libnetcdf-dev libhdf5-dev libpnetcdf-dev

# Dependencies for generating configuration scripts (Autoconf)
apt-get install -y m4 make gcc texinfo
```

### 3\. Installing IOR

The IOR installation process requires a few manual steps, notably updating Autoconf.

#### 3.1. Updating Autoconf

The default version of Autoconf available on Debian 11 is too old for IOR. A more recent version (\>= 2.71) must be compiled manually.

```bash
# Download and extract Autoconf 2.71
wget http://ftp.gnu.org/gnu/autoconf/autoconf-2.71.tar.gz
tar xf autoconf-2.71.tar.gz
cd autoconf-2.71

# Configure, compile, and install
./configure --prefix=/usr/local
make && sudo make install

# Return to the previous directory
cd ..
```

#### 3.2. Compiling IOR

Now that the environment is ready, we can clone and compile IOR.

```bash
# Clone the official IOR repository
git clone https://github.com/hpc/ior.git
cd ior

# Check the Autoconf version (must be >= 2.71)
autoconf --version

# Regenerate the configuration scripts with the new version of Autoconf
autoreconf -fi

# Export library paths so the configurator can find them
export CPPFLAGS="$(pkg-config --cflags hdf5)"
export LDFLAGS="$(pkg-config --libs hdf5)"

# Run the bootstrap script and configure the build with HDF5 and NCMPI backends
./bootstrap
MPICC=mpicc ./configure --with-hdf5=/usr --with-ncmpi

# Compile the project
make
```

### 4\. Running IOR Benchmarks

IOR can be used to simulate various workloads. Here is an example of a write test.

#### Execution Command

```bash
# Export these variables if you are running as root
export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1

# Run IOR with mpirun
mpirun -np 1 ~/ior/src/ior \
  -a POSIX \
  -b 256m -s 1 -t 512 \
  -w -i 1 \
  -o ior_256M_testfile \
  -k
```

#### Option Details

  - `-a POSIX`: Use the standard POSIX API (read/write).
  - `-b 256m`: Block size per process = 256 MiB.
  - `-s 1`: Number of segments (1 large block).
  - `-t 512`: Transfer size = 512 bytes. IOR will make multiple 512-byte transfers to write the 256 MiB block.
  - `-w`: Write mode.
  - `-i 1`: Number of test iterations.
  - `-o ior_256M_testfile`: Name of the test file.
  - `-k`: Keep the test file after execution.

### 5\. Capturing an I/O Trace with `strace`

To analyze IOR's behavior at the system call level, we use `strace`.

#### Capture Command

The following command runs a read test (`-r`) with random access (`-z`) and records all I/O-related system calls into a file named `trace.log`.

```bash
strace -yy -f -e trace=read,write,lseek,open,openat,creat,close,unlink \
  mpirun -np 1 ~/ior/src/ior \
    -a POSIX -b 256m -s 1 -t 512 \
    -r -i 1 -o ior_256M_testfile -k -z \
    > trace.log 2>&1
```

#### `strace` Options

  - `-yy`: Displays full details for file descriptors.
  - `-f`: Traces child processes as they are created.
  - `-e trace=...`: Specifies the exact list of system calls to monitor.

### 6\. Filtering and Formatting the Trace

The `trace.log` file generated by `strace` is verbose and not directly usable by our replay tool. A C filter script is used to parse it, extract the relevant information, and format it.

#### The Filtering Script

The provided C program (`filter_trace.c`) is designed to:

  - Read the `trace.log` file line by line.
  - Parse `lseek`, `read`, and `write` calls.
  - Keep track of the current offset (position) for each file descriptor.
  - Extract and format only the operations that match the IOR workload.

#### Detailed Operation

  - **Offset Tracking**: The script mimics the kernel's behavior by remembering the cursor position for each file. An `lseek` call directly updates this position. A `read` or `write` call uses the stored position as its offset and then increments it by the number of bytes transferred.
  - **Filtering Condition**: To isolate only the benchmark's I/O, the script applies a strict filter: it only prints operations where the size is exactly 512 bytes and the offset is a multiple of 512. This precisely matches the IOR test parameters (`-t 512`).
  - **Output Format**: The script generates a simple three-column text file that can be read by our replay tool:
      - **Operation\_Type**: 0 for read or 1 for write.
      - **Offset**: The starting position of the operation in bytes.
      - **Request\_Size**: The size of the operation (always 512 in our case).

#### Compilation and Usage

Save the C code provided into a file named `filter_trace.c`.
Compile the program with `gcc`:

```bash
gcc -o filter_trace filter_trace.c
```

Run the filter on your log and redirect the output to a new file:

```bash
./filter_trace trace.log > filtered_trace.txt
```

You now have the `filtered_trace.txt` file, ready for the next step.

### 7\. Replaying the Captured Trace

The custom tool `iortest_replay_fixed` is then used to replay the sequence of operations from `filtered_trace.txt` on a new data file.

#### Running the Replay Tool

```bash
# Replace /path/to/datafile with the path to the file on which to replay the trace
./iortest_replay_fixed --mode replay --trace-file filtered_trace.txt --data-file /path/to/datafile
```


