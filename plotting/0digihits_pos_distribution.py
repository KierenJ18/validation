# Load packages
import sys
import os
import awkward as ak
import numpy as np
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from packages.data_loading import load_validation_data, return_parent_params, discover_files, parent_params_cut, zero_digits_cut
from packages.plot_functions import plot_and_save_variable, plot_2d

detector = "HKFD"  # Set detector type
print(f"Detector set to: {detector}")
# Base directories
base_dir = "/vols/hyperk/users/kj4718/validation/analysed_results/" + detector
base_output_dir = "/vols/hyperk/users/kj4718/validation/plotting/" + detector

# Get all subdirectories
subfolders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]
print(f"Found subfolders: {subfolders}")

for subfolder in subfolders:
    print(f"\nProcessing subfolder: {subfolder}")
    input_folder = os.path.join(base_dir, subfolder, "wcsimrootevent")
    output_folder = os.path.join(base_output_dir, subfolder)

    # Check if wcsimrootevent folder exists
    if not os.path.exists(input_folder):
        print(f"Input folder {input_folder} does not exist. Skipping...")
        continue

    # Check if there are any .root files in wcsimrootevent folder
    root_files = [f for f in os.listdir(input_folder) if f.endswith('.root')]
    if not root_files:
        print(f"No .root files found in {input_folder}. Skipping...")
        continue

    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    try:
       # Load data
        per_event, per_trigger, per_file = load_validation_data(input_folder, max_files=100)
        parent_params = return_parent_params(per_event, detector=detector)
        zero_cut = zero_digits_cut(per_event, per_trigger)
        nonzero_cut = np.logical_not(zero_cut)
       
        # e_digit_hits = per_trigger["ndigihits"].compute()
        # ntrig_mask = per_event["ntriggers"].compute() == 1
        # zero_dig_mask = e_digit_hits[ntrig_mask] == 0
        # zero_dig_mask = [[m] for m in zero_dig_mask]
        # nonzero_dig_mask = np.logical_not(zero_dig_mask)
        # nonzero_dig_mask = [[m] for m in nonzero_dig_mask]

        x = ak.flatten(parent_params['pos_x'])[zero_cut]
        y = ak.flatten(parent_params['pos_y'])[zero_cut]
        z = ak.flatten(parent_params['pos_z'])[zero_cut]
        r = np.sqrt(ak.flatten(parent_params['radial_sq'])[zero_cut])

        x_1 = ak.flatten(parent_params['pos_x'])[nonzero_cut]
        y_1 = ak.flatten(parent_params['pos_y'])[nonzero_cut]
        z_1 = ak.flatten(parent_params['pos_z'])[nonzero_cut]
        r_1 = np.sqrt(ak.flatten(parent_params['radial_sq'])[nonzero_cut])

        if detector == "IWCD":
            r_cut = 325
            y_cut = 375
            in_tank_r = abs(r) <= r_cut
            in_tank_axis = abs(y) <= y_cut
        if detector == "HKFD":
            r_cut = 3530
            z_cut = 3260
            in_tank_r = abs(r) <= r_cut
            in_tank_axis = abs(z) <= z_cut
            
        parts = subfolder.split('_')    
        sample_name = f"{parts[0].upper()} {' '.join(parts[1:])}"     
        plot_2d(x, y, "x (cm)", "y (cm)", detector=detector, sample_name=sample_name,
                bins=(50, 50), show=False, outdir=output_folder,)
        if detector == "IWCD":
            plot_2d(y, r, "y (cm)", "r (cm)", detector=detector, sample_name=sample_name,
                    bins=(50, 50), show=False, outdir=output_folder,)
        if detector == "HKFD":
            plot_2d(z, r, "z (cm)", "r (cm)", detector=detector, sample_name=sample_name,
                    bins=(50, 50), show=False, outdir=output_folder,)
        
        # Plot various parameters
        print(f"Successfully processed {subfolder}")
        
    #print exception and line number
    except Exception as e:
        print(f"Error processing {subfolder}: {e} at line {sys.exc_info()[-1].tb_lineno}")
        continue
print(f"\nAll processing complete! Plots saved in {base_output_dir}")

