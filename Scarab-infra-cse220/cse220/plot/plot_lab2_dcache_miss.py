import os
import json
import argparse
import pandas as pd
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import csv
from matplotlib import cm


matplotlib.rc('font', size=14)

def read_descriptor_from_json(descriptor_filename):
    # Read the descriptor data from a JSON file
    try:
        with open(descriptor_filename, 'r') as json_file:
            descriptor_data = json.load(json_file)
        return descriptor_data
    except FileNotFoundError:
        print(f"Error: File '{descriptor_filename}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file '{descriptor_filename}': {e}")
        return None

def get_dcache(descriptor_data, sim_path, output_dir):
  benchmarks_org = descriptor_data["workloads_list"].copy()
  benchmarks = []
  dcache = {}

  try:
    for config_key in descriptor_data["configurations"].keys():
      dcache_config = []
      avg_dcache_config = 0.0
      cnt_benchmarks = 0
      for benchmark in benchmarks_org:
        benchmark_name = benchmark.split("/")
        exp_path = sim_path+'/'+benchmark+'/'+descriptor_data["experiment"]+'/'
        miss = 0.0
        hit = 0.0
        with open(exp_path+config_key+'/memory.stat.0.csv') as f:
          lines = f.readlines()
          for line in lines:
            if 'DCACHE_MISS_ONPATH_total_count' in line:
              tokens = [x.strip() for x in line.split(',')]
              miss = float(tokens[1])
              break
        
        with open(exp_path+config_key+'/memory.stat.0.csv') as f:
          lines = f.readlines()
          for line in lines:
            if 'DCACHE_HIT_total_count' in line:
              tokens = [x.strip() for x in line.split(',')]
              hit = float(tokens[1])
              break

        total = hit + miss
        if total == 0.0:
          ratio = 0.0
        else:
          ratio = miss/total

        avg_dcache_config += ratio

        cnt_benchmarks = cnt_benchmarks + 1
        if len(benchmarks_org) > len(benchmarks):
          benchmarks.append(benchmark_name)

        dcache_config.append(ratio)

      num = len(benchmarks)

      dcache_config.append(avg_dcache_config/num)
      dcache[config_key] = dcache_config

    benchmarks.append('Avg')
    plot_data(benchmarks, dcache, 'Dcache Miss Ratio', output_dir+'/FigureB.png')

  except Exception as e:
    print(e)

def plot_data(benchmarks, data, ylabel_name, fig_name, ylim=None):
  print(data)
  data_keys = data.keys()
  data_values = data.values()
  num_plots = 3
  for i in range(num_plots):
    print("Loop", i)
    # For dividing the data across a specific number of plots
    num_datapoints = math.ceil(len(benchmarks) / num_plots)
    lower_index = i * num_datapoints
    upper_index = min((i + 1) * num_datapoints, len(benchmarks))
    
    index_data = {}
    for key, value in data.items():
      index_data[key] = value[lower_index: upper_index]
    index_benchmarks = benchmarks[lower_index: upper_index]
    
    print("Plotting", i)
    # Original plotting code, modified for application
    colors = ['#800000', '#911eb4', '#4363d8', '#f58231', '#3cb44b', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#e6beff', '#e6194b', '#000075', '#800000', '#9a6324', '#808080', '#ffffff', '#000000']
    ind = np.arange(len(index_benchmarks))
    width = 0.1
    fig, ax = plt.subplots(figsize=(20, 4.4), dpi=80)
    num_keys = len(index_data.keys())

    idx = 0
    start_id = -int(num_keys/2)
    for key in index_data.keys():
      hatch=''
      if idx % 2:
        hatch='\\\\'
      else:
        hatch='///'
      ax.bar(ind + (start_id+idx)*width, index_data[key], width=width, fill=False, hatch=hatch, color=colors[idx], edgecolor=colors[idx], label=key)
      idx += 1
    plt.title(ylabel_name + " for Benchmarks")
    # plt.yscale('log')
    ax.set_xlabel("Benchmarks")
    ax.set_ylabel(ylabel_name)
    ax.set_xticks(ind)
    ax.set_xticklabels(index_benchmarks, rotation = 27, ha='right')
    ax.grid('x')
    if ylim != None:
      ax.set_ylim(ylim)
    ax.legend(loc="upper left", ncols=2)
    fig.tight_layout()

    index_figname = fig_name[:-4] + str(i) + fig_name [-4:]
    print("Saving plot!", index_figname)
    plt.savefig(index_figname, format="png", bbox_inches="tight")


if __name__ == "__main__":
    # Create a parser for command-line arguments
    parser = argparse.ArgumentParser(description='Read descriptor file name')
    parser.add_argument('-o','--output_dir', required=True, help='Output path. Usage: -o /home/$USER/plot/lab2_part_b')
    parser.add_argument('-d','--descriptor_name', required=True, help='Experiment descriptor name. Usage: -d /home/$USER/lab2.json')
    parser.add_argument('-s','--simulation_path', required=True, help='Simulation result path. Usage: -s /home/$USER/exp/simulations')

    args = parser.parse_args()
    descriptor_filename = args.descriptor_name

    descriptor_data = read_descriptor_from_json(descriptor_filename)
    get_dcache(descriptor_data, args.simulation_path, args.output_dir)
    plt.grid('x')
    plt.tight_layout()
    plt.show()
