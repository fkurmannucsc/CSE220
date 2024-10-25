#!/bin/bash
set -x #echo on
cd "$(dirname "$0")"

# Change this for new lab!
OUTPUT_DIR=/home/$USER/plot/lab2_part_b
SIM_PATH=/home/$USER/exp/simulations
DESCRIPTOR_PATH=/home/$USER/lab2test.json

mkdir -p $OUTPUT_DIR

# Lab 1 plots.
# python3 plot_ipc.py -o $OUTPUT_DIR -d $DESCRIPTOR_PATH -s $SIM_PATH
# python3 plot_misprediction.py -o $OUTPUT_DIR -d $DESCRIPTOR_PATH -s $SIM_PATH
# python3 plot_icache_miss.py -o $OUTPUT_DIR -d $DESCRIPTOR_PATH -s $SIM_PATH
# python3 plot_dcache_miss.py -o $OUTPUT_DIR -d $DESCRIPTOR_PATH -s $SIM_PATH

# Lab 2 plots.
# python3 plot_lab2_ipc.py -o $OUTPUT_DIR -d $DESCRIPTOR_PATH -s $SIM_PATH
# python3 plot_lab2_dcache_miss.py -o $OUTPUT_DIR -d $DESCRIPTOR_PATH -s $SIM_PATH

# Lab 2 plots, part B.
python3 plot_lab2_dcache_miss.py -o $OUTPUT_DIR -d $DESCRIPTOR_PATH -s $SIM_PATH
python3 plot_lab2_ccc.py -o $OUTPUT_DIR -d $DESCRIPTOR_PATH -s $SIM_PATH