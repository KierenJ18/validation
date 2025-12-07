#Import packages
import sys
import os
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from packages.data_loading import load_validation_data, return_parent_params, discover_files
from packages.plot_functions import plot_and_save_variable

detector = "HKFD"  # Set detector type
print(f"Detector set to: {detector}")

# Base directories
base_dir = "/vols/hyperk/users/kj4718/validation/analysed_results/" + detector
base_output_dir = "/vols/hyperk/users/kj4718/validation/plotting/" + detector

# Get all subdirectories
subfolders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
print(f"Found subfolders: {subfolders}")

# Gather valid datasets
valid_data = []
for subfolder in subfolders:
    input_folder = os.path.join(base_dir, subfolder, "wcsimrootevent")
    output_folder = os.path.join(base_output_dir, subfolder)
    
    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"Input folder {input_folder} does not exist. Skipping {subfolder}...")
        continue

    # Check for .root files in input folder
    root_files = [f for f in os.listdir(input_folder) if f.endswith('.root')]
    if not root_files:
        print(f"No .root files found in {input_folder}. Skipping {subfolder}...")
        continue

    try:
        per_event, per_trigger, per_file = load_validation_data(input_folder, max_files=100)
        parent_params = return_parent_params(per_event, detector=detector)

        parts = subfolder.split('_')
        sample_name = f"{parts[0].upper()} {' '.join(parts[1:])}"
        # store necessary info for combined plotting
        valid_data.append({
            "subfolder": subfolder,
            "input_folder": input_folder,
            "output_folder": output_folder,
            "parent_params": parent_params,
            "sample_name": sample_name,
        })
        
        # ensure per-subfolder output dir exists
        os.makedirs(output_folder, exist_ok=True)
        print(f"Loaded {subfolder}")
        
    except Exception as e:
        print(f"Error loading {subfolder}: {e}")
        continue

if not valid_data:
    print("No valid datasets found. Exiting.")
    raise SystemExit(0)

# Define x-axis labels for plots (keep in sync with parent_params keys order)
x_labels = ["Azimuth (deg)", "Direction $x$ (cm)", "Direction $y$ (cm)", "Direction $z$ (cm)",
            "Position $x$ (cm)", "Position $y$ (cm)", "Position $z$ (cm)", "Radial Distance Squared (m$^2$)",
            "Energy (MeV)"]

# Determine keys from first dataset
first_keys = list(valid_data[0]["parent_params"].keys())

# For each variable/key produce one merged plot overlaying all datasets
for i in range(len(first_keys) - 1):
    key = first_keys[i + 1]
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    for entry in valid_data:
        arr = entry["parent_params"].get(key)
        if arr is None:
            print(f"Key {key} not found for {entry['subfolder']}, skipping.")
            continue
        
        # plot directly on the shared axes (no per-dataset file saved here)
        ax.hist(arr, bins=25, histtype='step', label=entry["sample_name"])
    
    xlabel = x_labels[i] if i < len(x_labels) else key
    title = f"{detector} {key}"
    ax.set_title(title, size=22)
    ax.set_xlabel(xlabel, size=20)
    ax.set_ylabel("# Entries", size=20)
    
    ax.legend()
    plt.tight_layout()
    save_name = f"{detector}_{key}".replace(" ", "_") + ".png"
    os.makedirs(base_output_dir+' merged_plots', exist_ok=True)
    fig.savefig(os.path.join(base_output_dir+' merged_plots', save_name))
    plt.close(fig)
print(f"Saved merged plots to {base_output_dir+' merged_plots'}")
