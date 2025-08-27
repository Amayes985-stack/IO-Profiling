#!/bin/bash

# Check if the script is run with the correct number of arguments.
# The script expects 2 or 3 arguments.
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    # If the number of arguments is incorrect, display the usage message and exit.
    echo "Usage: $0 <log_dir> <type> [<optional_arg>]"
    echo "Type: baseline or <sz_bloc>"
    exit 1
fi

# Assign command-line arguments to variables.
LOG_DIR=$1          # The directory containing the log files.
TYPE=$2             # The type of plot to generate (e.g., baseline or block size).
OPTIONAL_ARG=$3     # An optional argument for additional plotting options.

# Define the directory containing the plotting scripts.
SCRIPT_DIR=$(dirname "$0")/script/plot
BOXPLOT_DIR=$SCRIPT_DIR

# Check if the optional argument is provided and equals "nb_run".
if [ -n "$OPTIONAL_ARG" ] && [ "$OPTIONAL_ARG" == "nb_run" ]; then
    # If the optional argument is "nb_run", run the plot_io_all_run.py script.
    echo "Optional argument given, plotting in interactive mode all runs from each iteration (1000 to 1600 IO) : $OPTIONAL_ARG"
    python3 $SCRIPT_DIR/plot_io_all_run.py $LOG_DIR $TYPE

# If the optional argument is provided but not "nb_run", show an error message and exit.
elif [ -n "$OPTIONAL_ARG" ] && [ "$OPTIONAL_ARG" != "nb_run" ]; then
    echo "Wrong optional argument given: $OPTIONAL_ARG. Try: nb_run (WARNING: THIS ARGUMENT USES INTERACTIVE BACKEND MODE FOR PLOTTING)"
    exit 1
    
# If the TYPE argument is "baseline", run the plot_baseline.py script.
elif [ "$TYPE" == "baseline" ]; then
    python3 $SCRIPT_DIR/plot_baseline.py $LOG_DIR

# If the TYPE argument is "plot_all", run several plotting scripts for different block sizes.
elif [ "$TYPE" == "plot_all" ]; then
    python3 $SCRIPT_DIR/plot_baseline_passive.py $LOG_DIR
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 1s
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 8k
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 16k
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 128k
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 512k
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 1M
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 2M
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 4M
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 8M

# If the TYPE argument is "box_baseline", run the box_plot_baseline.py script.
elif [ "$TYPE" == "box_baseline" ]; then
    python3 $SCRIPT_DIR/box_plot_baseline.py $LOG_DIR

# If the TYPE argument is "box_all", run several box plot scripts for different block sizes.
elif [ "$TYPE" == "box_all" ]; then
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 1s
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 8k
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 16k
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 128k
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 512k
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 1M
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 2M
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 4M
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 8M

# If the TYPE argument is "all", run a combination of baseline and IO plotting scripts.
elif [ "$TYPE" == "all" ]; then
    python3 $SCRIPT_DIR/plot_baseline_passive.py $LOG_DIR

    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 1s
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 8k
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 16k
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 128k
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 512k
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 1M
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 2M
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 4M
    python3 $SCRIPT_DIR/plot_io_passive.py $LOG_DIR 8M

    python3 $SCRIPT_DIR/box_plot_baseline.py $LOG_DIR

    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 1s
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 8k
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 16k
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 128k
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 512k
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 1M
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 2M
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 4M
    python3 $SCRIPT_DIR/box_plot_io.py $LOG_DIR 8M

# If the TYPE argument is "all_run", run several scripts for plotting all runs in passive mode.
elif [ "$TYPE" == "all_run" ]; then
    python3 $SCRIPT_DIR/plot_baseline_passive.py $LOG_DIR
    python3 $SCRIPT_DIR/plot_io_all_run_passive.py $LOG_DIR 1s
    python3 $SCRIPT_DIR/plot_io_all_run_passive.py $LOG_DIR 8k
    python3 $SCRIPT_DIR/plot_io_all_run_passive.py $LOG_DIR 16k
    python3 $SCRIPT_DIR/plot_io_all_run_passive.py $LOG_DIR 128k
    python3 $SCRIPT_DIR/plot_io_all_run_passive.py $LOG_DIR 512k
    python3 $SCRIPT_DIR/plot_io_all_run_passive.py $LOG_DIR 1M
    python3 $SCRIPT_DIR/plot_io_all_run_passive.py $LOG_DIR 2M
    python3 $SCRIPT_DIR/plot_io_all_run_passive.py $LOG_DIR 4M
    python3 $SCRIPT_DIR/plot_io_all_run_passive.py $LOG_DIR 8M

# If none of the specific conditions match, default to running the plot_io.py script with the provided type.
else
    python3 $SCRIPT_DIR/plot_io.py $LOG_DIR $TYPE
fi

