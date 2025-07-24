import os
import yaml
from packages.validation_functions import load_validation_data, get_cut_params


def load_dataset(config_path, dataset_name):
    # Read YAML config
    with open(config_path) as f:
        config = yaml.safe_load(f)
    ds = config["datasets"][dataset_name]
    folder = ds["folder"]
    events_per_file = ds["events_per_file"]
    root_files = sorted([os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".root")])
    per_event, per_trigger, per_file = load_validation_data(root_files, events_per_file)
    cut_params = get_cut_params(per_event)
    return per_event, per_trigger, per_file, cut_params