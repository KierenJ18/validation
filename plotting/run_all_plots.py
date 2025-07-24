import yaml
from packages.data_loading import load_dataset
from packages.plotting import plot_energy

with open("config.yaml") as f:
    config = yaml.safe_load(f)

for name, ds in config["datasets"].items():
    print(f"Processing {name}...")
    cut_params = load_dataset(ds["folder"], ds["events_per_file"])
    plot_energy(cut_params, ds["label"], ds["color"])