# plot_functions.py
"""
Functions for generating standard and custom plots for validation samples.
"""

import matplotlib.pyplot as plt

def plot_variable(array, sample_name, detector, var_name, bins=50, xlabel=None, ylabel="Frequency", cut_applied=False):
    plt.figure()
    plt.hist(array, bins=bins)
    cut_str = " (cut applied)" if cut_applied else ""
    plt.title(f"{var_name}: {sample_name} ({detector}){cut_str}")
    plt.xlabel(xlabel if xlabel else var_name)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.show()

def plot_all_per_event(per_event, sample_name, detector, cut=None):
    # Variables from per_event
    event_vars = [
        "track_energy", "track_startpos", "track_dir", "track_flag", "track_parentid",
        "nrawhits", "hittime", "hittime_photon", "hittime_noise", "ntriggers"
    ]
    for var in event_vars:
        arr = per_event[var]
        # Apply cut for variables that need it
        if cut is not None and var in ["track_energy", "track_startpos", "track_dir", "track_flag", "track_parentid"]:
            arr = arr[cut]
            cut_applied = True
        else:
            cut_applied = False
        # Flatten awkward arrays if needed
        try:
            import awkward as ak
            arr = ak.flatten(arr)
        except Exception:
            pass
        plot_variable(arr, sample_name, detector, var, cut_applied=cut_applied)

def plot_all_per_trigger(per_trigger, sample_name, detector):
    trigger_vars = [
        'eventnumber', 'triggernumber', 'ndigihits', 'totaldigipe', 'digitime', 'digitime_photon', 'digitime_noise', 'digitime_photon', 'digitime_mix', 'ndigihitstrigger', 'triggertime', 'digiplustriggertime'
    ]
    for var in trigger_vars:
        arr = per_trigger[var]
        try:
            import awkward as ak
            arr = ak.flatten(arr)
        except Exception:
            pass
        plot_variable(arr, sample_name, detector, var)

def plot_all_per_file(per_file, sample_name, detector):
    file_vars = ['npmt20', 'npmtm', 'npmtod', 'WCCylRadius', 'WCCylLength']
    for var in file_vars:
        arr = per_file[var]
        try:
            import awkward as ak
            arr = ak.flatten(arr)
        except Exception:
            pass
        plot_variable(arr, sample_name, detector, var)

def plot_all(per_event, per_trigger, per_file, sample_name, detector, cut=None):
    plot_all_per_event(per_event, sample_name, detector, cut)
    plot_all_per_trigger(per_trigger, sample_name, detector)
    plot_all_per_file(per_file, sample_name, detector)
