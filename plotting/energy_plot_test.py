import argparse
import packages.plotting as plot
import packages.data_loading as dl
import awkward as ak

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="YAML config file")
    parser.add_argument("--dataset", required=True, help="Dataset name in YAML")
    parser.add_argument("--output-dir", default=".", help="Directory to save plots")
    parser.add_argument("--no-show", action="store_true", help="Do not display plots")
    parser.add_argument("--save", action="store_true", help="Save plots to file")
    args = parser.parse_args()

    # Load data using YAML config and dataset name
    per_event, _, _, cut_params = dl.load_dataset(args.config, args.dataset)

    plot.plot_energy(
        cut_params,
        output_path=args.output_dir,
        show=not args.no_show,
        label="hkfd_id_e",
        color="blue"
    )