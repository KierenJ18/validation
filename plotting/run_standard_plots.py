# run_standard_plots.py
"""
Script to run standard plots for all samples and detectors.
"""
from packages.data_loading import load_sample
from plotting.plot_functions import plot_per_event, plot_per_trigger, plot_per_file

SAMPLES = [
    "id_elneg", "id_elpos", "id_gamma_conv", "id_muneg", "id_muneg_78off", "id_mupos", "id_mupos_78off",
    "id_pi0", "id_pineg", "id_pineg_6off", "id_pipos", "id_pipos_6off",
    "idod_elneg", "idod_elpos", "idod_gamma_conv", "idod_muneg", "idod_muneg_78off", "idod_mupos", "idod_mupos_78off",
    "idod_pi0", "idod_pineg", "idod_pineg_6off", "idod_pipos", "idod_pipos_6off"
]
DETECTORS = ["HKFD", "IWCD"]
BASE_DIR = "/vols/hyperk/users/kj4718/validation/analysed_results"  # Update as needed

for detector in DETECTORS:
    for sample in SAMPLES:
        try:
            data = load_sample(sample, detector, BASE_DIR)
            plot_per_event(data, sample, detector)
            plot_per_trigger(data, sample, detector)
            plot_per_file(data, sample, detector)
        except Exception as e:
            print(f"Error processing {sample} ({detector}): {e}")
