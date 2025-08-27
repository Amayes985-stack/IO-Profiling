# IO-Profiling : Energy Consumption Analysis for IO Operations

Welcome to the repository for my internship project focused on the analysis of energy consumption during input/output (IO) operations. This project includes a set of scripts and tools designed to calculate, visualize, and compare energy consumption using different methods. The main goal is to determine the most accurate approach for measuring energy consumed by IO operations, specifically focusing on projections and averages as well as combining them with IOR

-----

## Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Installation](#installation)
4. [Usage](#usage)
   - [Example: Compiling and Running iotest.c](#example-compiling-and-running-iotestc)
   - [Running the iotest Benchmark](#running-the-iotest-benchmark)
   - [Running the ior_bench.sh Benchmark](#running-the-ior-benchsh-benchmark)
   - [Plotting Results](#plotting-results)
5. [Scripts Explanation](#scripts-explanation)
   - [iotest.c and iotest.h](#iotestc-and-iotesth)
   - [benchmark.sh](#benchmarksh)
   - [ior_bench.sh](#ior_bench)
   - [plotting.sh](#plottingsh)
   - [format.sh](#formatsh)
   - [New Scripts and Tools](#new-scripts-and-tools)
6. [Guide to Installing and Using IOR for I/O Performance Analysis](#guide-to-installing-and-using-ior-for-io-performance-analysis)
   - [1. Environment Setup](#1-environment-setup)
   - [2. Installing Dependencies](#2-installing-dependencies)
   - [3. Installing IOR](#3-installing-ior)
   - [4. Running IOR Benchmarks](#4-running-ior-benchmarks)
   - [5. Capturing an I/O Trace with strace](#5-capturing-an-io-trace-with-strace)
   - [6. Filtering and Formatting the Trace](#6-filtering-and-formatting-the-trace)
   - [7. Replaying the Captured Trace](#7-replaying-the-captured-trace)

-----

## Project Overview

This project was developed during my internship and aims to analyze energy consumption during IO operations on storage devices. The focus is on calculating the exact energy consumed using wattmeter readings and comparing these calculations using different methods such as projection and average energy methods. The scripts automate the entire process from data collection to analysis and visualization.

-----

## Project Structure

The project is organized as follows:

```
├── benchmark.sh            # Script for running IO benchmarks
├── format.sh               # Script for formatting and processing raw data
├── plotting.sh             # Script for plotting raw data
├── logs/                   # Directory containing raw and processed data files
├── scripts/                # Directory containing all Python and Shell scripts
│   ├── plot/               # Directory containing scripts for plotting
│       └── ...
│   ├── format/             # Directory containing scripts for formatting
│       └── ...
│   ├── math/               # Directory containing scripts for mathematical computations
│       └── normalize.py    # Script to calculate normalized offsets
│       └── frequency.py    # Script to display frequency distributions
│       └── ...             
│   └── IOR/                # Directory containing IOR-related tools
│       └── iortest1.c      # C program based on iotest with IOR trace functionality
│       └── filter_traces.c # C program for filtering IOR traces
├── README.md
```

-----

## Usage

### Example: Compiling and Running iotest.c

The iotest.c file is a C program used to simulate IO operations. The associated header file, iotest.h, contains the definitions and functions used within the iotest.c file.

#### Compiling iotest.c

```bash
gcc -g iotest.c -o iotest -lm
```

This command compiles the C code and creates an executable named `iotest`.

### Running the iotest Benchmark

The benchmark.sh script is used to run IO operations and measure energy consumption. Here's an example of how to run the benchmark:

```bash
sudo-g5k ./benchmark.sh READ RAND HDD
```

This script runs the IO benchmark with specified parameters (READ or WRITE mode, RANDOM or SEQUENTIAL (RAND or SEQ) access pattern, HDD or SSD storage type) and stores the results in the `logs/` directory.

### Running the ior_bench.sh Benchmark

The ior_bench.sh script is a specialized benchmark for measuring energy consumption using iortest1.c. It's designed to test different read/write ratios and file sizes, and it captures energy data directly via the Grid5000 API.

#### Execution Command

This script takes one argument: the storage type (HDD or SSD).

```bash
./ior_bench.sh <storage_type>
```

For example, to run the benchmark on an HDD:

```bash
./ior_bench.sh HDD
```

### Plotting Script (plotting.sh)

The plotting.sh script is used to generate various plots from the benchmark results. It supports different types of plots, such as baseline plots, boxplots, and IO energy consumption plots.

#### Usage Example:

```bash
./plotting.sh <log_dir> <type> [<optional_arg>]
```

- `log_dir`: The directory containing log files at the base of the logs (see example below).  
- `type`: The type of plot to generate (e.g., baseline or sz_bloc).  
- `optional_arg`: An optional argument to specify additional options (e.g., nb_run).  

For example, to generate ALL plot for all runs per iteration:

```bash
./plotting.sh logs/HDD/READ/RAND/ plot_all nb_run
```

-----

## Scripts Explanation

### iotest.c and iotest.h

- **iotest.c**: This C program simulates IO operations by reading and writing data to a storage device.  
- **iotest.h**: The header file contains function prototypes, macros, and structure definitions used in iotest.c.

### benchmark.sh

Automates the process of running IO benchmarks on different storage devices.

### ior_bench.sh

Automates running IO benchmarks on different storage devices using the **IOR library**.

### plotting.sh

Generates visual plots of the energy consumption data collected during the benchmarks.

### format.sh

Organizes and formats raw data collected during IO tests.  

#### Usage

```bash
./format.sh <directory_to_move>
```

-----

### New Scripts and Tools

#### scripts/IOR/

- **iortest1.c**: Modified iotest.c including IOR trace functionality.  
- **filter_traces.c**: Parses raw trace data and formats it for replay.

#### scripts/math/

- **normalize.py**: Calculates normalized offsets for IO operations.  
- **frequency.py**: Displays the frequency distribution of IO requests.

-----

## Guide to Installing and Using IOR for I/O Performance Analysis

### 1. Environment Setup

Interactive node reservation using OAR:

```bash
oarsub -I -l host=1,walltime=7:00 -q default -p taurus -t deploy
```

#### Operating System Deployment

```bash
kadeploy3 debian11-big
```

### 2. Installing Dependencies

```bash
apt-get update
apt-get install -y build-essential openmpi-bin
apt-get install -y libnetcdf-dev libhdf5-dev libpnetcdf-dev
apt-get install -y m4 make gcc texinfo
```

### 3. Installing IOR

#### 3.1 Updating Autoconf

```bash
wget http://ftp.gnu.org/gnu/autoconf/autoconf-2.71.tar.gz
tar xf autoconf-2.71.tar.gz
cd autoconf-2.71
./configure --prefix=/usr/local
make && sudo make install
cd ..
```

#### 3.2 Compiling IOR

```bash
git clone https://github.com/hpc/ior.git
cd ior
autoconf --version
autoreconf -fi
export CPPFLAGS="$(pkg-config --cflags hdf5)"
export LDFLAGS="$(pkg-config --libs hdf5)"
./bootstrap
MPICC=mpicc ./configure --with-hdf5=/usr --with-ncmpi
make
```

### 4. Running IOR Benchmarks

```bash
export OMPI_ALLOW_RUN_AS_ROOT=1
export OMPI_ALLOW_RUN_AS_ROOT_CONFIRM=1
mpirun -np 1 ~/ior/src/ior   -a POSIX   -b 256m -s 1 -t 512   -w -i 1   -o ior_256M_testfile   -k
```

### 5. Capturing an I/O Trace with strace

```bash
strace -yy -f -e trace=read,write,lseek,open,openat,creat,close,unlink   mpirun -np 1 ~/ior/src/ior     -a POSIX -b 256m -s 1 -t 512     -r -i 1 -o ior_256M_testfile -k -z     > trace.log 2>&1
```

### 6. Filtering and Formatting the Trace

```bash
gcc -o filter_trace filter_trace.c
./filter_trace trace.log > filtered_trace.txt
```

### 7. Replaying the Captured Trace

```bash
./iortest_replay_fixed --mode replay --trace-file filtered_trace.txt --data-file /path/to/datafile
```