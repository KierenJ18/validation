import uproot
import awkward as ak
import numpy as np


import os

def discover_files(folder, event_numbers=None, max_events=None):
    """
    Discover files in a folder, optionally filtering by event numbers or limiting to max_events.
    """
    all_files = sorted([os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.root')])
    if event_numbers is not None:
        # Filter files by event numbers in their filename
        filtered = []
        for f in all_files:
            for ev in event_numbers:
                if f"{ev:04d}" in f:
                    filtered.append(f)
        all_files = filtered
    if max_events is not None:
        all_files = all_files[:max_events]
    return all_files

def read_event_numbers_from_txt(txt_path):
    with open(txt_path, 'r') as f:
        return [int(line.strip()) for line in f if line.strip().isdigit()]

def load_validation_data(
    folder_or_files,
    max_events=None,
    single_event=None,
    event_txt=None
):
    """
    Load validation data flexibly.
    Args:
        folder_or_files: str (folder path) or list of file paths
        max_events: int, limit number of events/files
        single_event: int, load only files for this event number
        event_txt: str, path to txt file with event numbers to load
    Returns:
        per_event, per_trigger, per_file
    """
    if isinstance(folder_or_files, str):
        folder = folder_or_files
        event_numbers = None
        if event_txt:
            event_numbers = read_event_numbers_from_txt(event_txt)
        elif single_event is not None:
            event_numbers = [single_event]
        files = discover_files(folder, event_numbers=event_numbers, max_events=max_events)
    else:
        files = folder_or_files
        if max_events is not None:
            files = files[:max_events]

    # uproot concatenate expects a dict of {tuple(files): tree_name}
    file_tuple = tuple(files)
    per_event = uproot.concatenate(
        {file_tuple: "validation_per_event"},
        ["track_energy", "track_startpos", "track_dir", "track_flag", "track_parentid",
         "nrawhits", "hittime", "hittime_photon", "hittime_noise", "ntriggers"])
    per_trigger = uproot.concatenate(
        {file_tuple: "validation_per_trigger"},
        ['eventnumber', 'triggernumber', 'ndigihits', 'totaldigipe', 'digitime', 'digitime_photon', 'digitime_noise', 'digitime_photon', 'digitime_mix', 'ndigihitstrigger', 'triggertime', 'digiplustriggertime'])
    per_file = uproot.concatenate(
        {file_tuple: "validation_per_file"},
        ['npmt20', 'npmtm', 'npmtod', 'WCCylRadius', 'WCCylLength'])

    return per_event, per_trigger, per_file

    # Example usage:
    # mu_per_event, mu_per_trigger, mu_per_file = load_validation_data("mu", mu_full_paths, events)


def get_parent(per_event):
    flag = per_event["track_flag"]
    parentid = per_event["track_parentid"]
    parent_cut = (parentid == 0) & (flag >= 0)
    return parent_cut

def load_validation_data(
    folder_or_files,
    max_events=None,
    single_event=None,
    event_txt=None,
    return_parent_params=False
):
    """
    Load validation data flexibly.
    Args:
        folder_or_files: str (folder path) or list of file paths
        max_events: int, limit number of events/files
        single_event: int, load only files for this event number
        event_txt: str, path to txt file with event numbers to load
        return_parent_params: bool, whether to return parent cut and params
    Returns:
        per_event, per_trigger, per_file[, parent_params]
    """
    if isinstance(folder_or_files, str):
        folder = folder_or_files
        event_numbers = None
        if event_txt:
            event_numbers = read_event_numbers_from_txt(event_txt)
        elif single_event is not None:
            event_numbers = [single_event]
        files = discover_files(folder, event_numbers=event_numbers, max_events=max_events)
    else:
        files = folder_or_files
        if max_events is not None:
            files = files[:max_events]

    file_tuple = tuple(files)
    per_event = uproot.concatenate(
        {file_tuple: "validation_per_event"},
        ["track_energy", "track_startpos", "track_dir", "track_flag", "track_parentid",
         "nrawhits", "hittime", "hittime_photon", "hittime_noise", "ntriggers"])
    per_trigger = uproot.concatenate(
        {file_tuple: "validation_per_trigger"},
        ['eventnumber', 'triggernumber', 'ndigihits', 'totaldigipe', 'digitime', 'digitime_photon', 'digitime_noise', 'digitime_photon', 'digitime_mix', 'ndigihitstrigger', 'triggertime', 'digiplustriggertime'])
    per_file = uproot.concatenate(
        {file_tuple: "validation_per_file"},
        ['npmt20', 'npmtm', 'npmtod', 'WCCylRadius', 'WCCylLength'])

    if return_parent_params:
        # Flatten everything first to ensure consistent indexing
        flag = ak.flatten(per_event["track_flag"])
        parentid = ak.flatten(per_event["track_parentid"])
        directions = ak.flatten(per_event["track_dir"])
        start_pos = ak.flatten(per_event["track_startpos"])
        energy = ak.flatten(per_event["track_energy"])

        parent_cut = (parentid == 0) & (flag >= 0)

        dir_x = directions["fX"][parent_cut]
        dir_y = directions["fY"][parent_cut]
        dir_z = directions["fZ"][parent_cut]
        azimuth = np.arctan2(dir_y, dir_x)

        pos_x = start_pos["fX"][parent_cut]
        pos_y = start_pos["fY"][parent_cut]
        pos_z = start_pos["fZ"][parent_cut]
        radial_sq = pos_x**2 + pos_z**2

        energy_cut = energy[parent_cut]

        parent_params = {
            "cut": parent_cut,
            "azimuth": azimuth,
            "dir_x": dir_x,
            "dir_y": dir_y,
            "dir_z": dir_z,
            "pos_x": pos_x,
            "pos_y": pos_y,
            "pos_z": pos_z,
            "radial_sq": radial_sq,
            "energy": energy_cut
        }
        return per_event, per_trigger, per_file, parent_params
    else:
        return per_event, per_trigger, per_file
