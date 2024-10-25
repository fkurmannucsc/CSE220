import os
import json
import argparse
import pandas as pd
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

def get_ccc(descriptor_data, sim_path, output_dir):
  benchmarks_org = descriptor_data["workloads_list"].copy()
  benchmarks = []
  capacity_dict = {}
  conflict_dict = {}
  compulsory_dict = {}

  try:
    for config_key in descriptor_data["configurations"].keys():
      capacity_config = []
      conflict_config = []
      compulsory_config = []

      avg_capacity = 0.0
      avg_conflict = 0.0
      avg_compulsory = 0.0

      cnt_benchmarks = 0
      for benchmark in benchmarks_org:
        benchmark_name = benchmark.split("/")
        exp_path = sim_path+'/'+benchmark+'/'+descriptor_data["experiment"]+'/'
        capacity = 0.0
        conflict = 0.0
        compulsory = 0.0

        with open(exp_path+config_key+'/memory.stat.0.csv') as f:
          lines = f.readlines()
          for line in lines:
            if 'DCACHE_MISS_ONPATH_COMPULSORY_count' in line:
              tokens = [x.strip() for x in line.split(',')]
              compulsory = float(tokens[1])
              break
        
        with open(exp_path+config_key+'/memory.stat.0.csv') as f:
          lines = f.readlines()
          for line in lines:
            if 'DCACHE_MISS_ONPATH_CAPACITY_count' in line:
              tokens = [x.strip() for x in line.split(',')]
              capacity = float(tokens[1])
              compulsory += float(tokens[1])
              break
        
        with open(exp_path+config_key+'/memory.stat.0.csv') as f:
          lines = f.readlines()
          for line in lines:
            if 'DCACHE_MISS_ONPATH_CONFLICT_count' in line:
              tokens = [x.strip() for x in line.split(',')]
              conflict = float(tokens[1])
              capacity += float(tokens[1])
              compulsory += float(tokens[1])
              break

        avg_capacity += capacity
        avg_conflict += conflict
        avg_compulsory += compulsory

        cnt_benchmarks = cnt_benchmarks + 1
        if len(benchmarks_org) > len(benchmarks):
          benchmarks.append(benchmark_name)

        capacity_config.append(capacity)
        conflict_config.append(conflict)
        compulsory_config.append(compulsory)

      num = len(benchmarks)

      capacity_config.append(avg_capacity/num)
      conflict_config.append(avg_conflict/num)
      compulsory_config.append(avg_compulsory/num)

      capacity_dict[config_key] = capacity_config
      conflict_dict[config_key] = conflict_config
      compulsory_dict[config_key] = compulsory_config

    # ccc = {}
    # for key in capacity_dict:
    #   ccc[key] = {"capacity": capacity_dict[key], "conflict": conflict_dict[key], "compulsory": compulsory_dict[key]}

    ccc = {"conflict": conflict_dict, "capacity": capacity_dict, "compulsory": compulsory_dict}
    benchmarks.append('Avg')
    plot_data(benchmarks, ccc, 'Dcache C,C,C Distribution', output_dir+'/FigureCCC.png')

  except Exception as e:
    print(e)

def plot_data(benchmarks, data, ylabel_name, fig_name, ylim=None):
  print(data)
  colors = ['#800000', '#911eb4', '#4363d8', '#f58231', '#3cb44b', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#e6beff', '#e6194b', '#000075', '#800000', '#9a6324', '#808080', '#ffffff', '#000000']
  ind = np.arange(len(benchmarks))
  width = 0.18
  fig, ax = plt.subplots(figsize=(14, 4.4), dpi=80)
  fig.stacked = True
  num_keys = len(data.keys())
  
  outer_idx = 0
  start_id = -int(num_keys/2)
  for key, value in reversed(data.items()):
    print(key, value)
    idx = 0

    for inner_key, inner_value in value.items():
      ax.bar(ind + (start_id+idx)*width, inner_value, width=width, fill=True, color=colors[outer_idx])
      idx += 1

    outer_idx += 1    

  plt.title(ylabel_name + " for Benchmarks")
  ax.set_xlabel("Benchmarks")
  ax.set_ylabel(ylabel_name)
  ax.set_xticks(ind)
  ax.set_xticklabels(benchmarks, rotation = 27, ha='right')
  ax.grid('x')

  if ylim != None:
    ax.set_ylim(ylim)
  ax.legend(loc="upper left", ncols=2)
  fig.tight_layout()
  print("Saving plot!")
  plt.savefig(fig_name, format="png", bbox_inches="tight")


if __name__ == "__main__":
    # Create a parser for command-line arguments
    parser = argparse.ArgumentParser(description='Read descriptor file name')
    parser.add_argument('-o','--output_dir', required=True, help='Output path. Usage: -o /home/$USER/plot/lab2_part_b')
    parser.add_argument('-d','--descriptor_name', required=True, help='Experiment descriptor name. Usage: -d /home/$USER/lab2.json')
    parser.add_argument('-s','--simulation_path', required=True, help='Simulation result path. Usage: -s /home/$USER/exp/simulations')

    args = parser.parse_args()
    descriptor_filename = args.descriptor_name

    descriptor_data = read_descriptor_from_json(descriptor_filename)
    get_ccc(descriptor_data, args.simulation_path, args.output_dir)
    plt.grid('x')
    plt.tight_layout()
    plt.show()
