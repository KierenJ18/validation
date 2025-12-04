# Load packages
import sys
import os
import matplotlib.pyplot as plt
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from packages.data_loading import load_validation_data, return_parent_params, discover_files
from packages.plot_functions import plot_and_save_variable

detector = "IWCD"  # Set detector type
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
        
        # Define x-axis labels for plots
        x_labels = ["Azimuth (deg)", "Direction $x$ (cm)", "Direction $y$ (cm)", "Direction $z$ (cm)",
                    "Position $x$ (cm)", "Position $y$ (cm)", "Position $z$ (cm)", "Radial Distance Squared (m$^2$)",
                    "Energy (MeV)"]
        
        # Plot various parameters
        for i in range(len(parent_params.keys()) - 1):
            list_keys = list(parent_params.keys())

            # Create a readable sample name from subfolder
            parts = subfolder.split('_')
            sample_name = f"{parts[0].upper()} {' '.join(parts[1:])}" 

            #Getting detector name
            detector = os.path.basename(base_dir)

            plot_and_save_variable(
                parent_params[list_keys[i + 1]],
                var_name=list_keys[i + 1],
                sample_name=sample_name,
                detector=detector,
                outdir=output_folder,
                xlabel=x_labels[i],
                ylabel="# Entries"
            )
        print(f"Successfully processed {subfolder}")

    except Exception as e:
        print(f"Error processing {subfolder}: {e}")
        continue
print(f"\nAll processing complete! Plots saved in {base_output_dir}")

