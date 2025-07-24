import matplotlib.pyplot as plt
import awkward as ak

import numpy as np

def plot_position_distributions(
    per_event,
    onedim=True,
    twodim=False,
    output_path=None,
    show=True
):
    """
    Plots position distributions from per_event dictionary.
    Args:
        per_event (dict): Dictionary with keys 'pos_x', 'pos_y', 'pos_z'.
        onedim (bool): If True, plot 1D histograms for each axis.
        twodim (bool): If True, plot 2D histograms for X vs Y and X vs Z.
        output_path (str): If provided, save the plot to this path.
        show (bool): If True, display the plot.
    """
    if onedim:
        for axis in ["pos_x", "pos_y", "pos_z"]:
            plt.hist(per_event[axis], bins=50, histtype="step", color="blue", linewidth=1.5, label="Electrons")
            plt.xlabel(f"{axis[-1].upper()} Position (cm)")
            plt.ylabel("# Entries")
            plt.title(f"HKFD {axis[-1].upper()} Position Distribution")
            plt.xticks(np.linspace(-max(per_event[axis]), max(per_event[axis]), 9), rotation=45)
            plt.legend()
            plt.tight_layout()
            if output_path:
                plt.savefig(f"{output_path}_{axis}.png")
            if show:
                plt.show()
            plt.close()
    if twodim:
        # 2D histogram for X vs Y
        plt.hist2d(ak.to_numpy(per_event["pos_x"]), ak.to_numpy(per_event["pos_y"]), bins=50)
        plt.xlabel("X (cm)")
        plt.ylabel("Y (cm)")
        plt.title("X vs Y Position Distribution")
        plt.colorbar(label="# Entries")
        plt.tight_layout()
        if output_path:
            plt.savefig(f"{output_path}_xy.png")
        if show:
            plt.show()
        plt.close()

        # 2D histogram for X vs Z
        plt.hist2d(ak.to_numpy(per_event["pos_x"]), ak.to_numpy(per_event["pos_z"]), bins=50)
        plt.xlabel("X (cm)")
        plt.ylabel("Z (cm)")
        plt.title("X vs Z Position Distribution")
        plt.colorbar(label="# Entries")
        plt.tight_layout()
        if output_path:
            plt.savefig(f"{output_path}_xz.png")
        if show:
            plt.show()
        plt.close()

def plot_energy(per_event, label, color, output_path=None, show=True):
    plt.hist(per_event["energy"], bins=50, histtype="step", color=color, label=label)
    plt.xlabel("Energy (MeV)")
    plt.ylabel("# Entries")
    plt.title(f"{label} Energy Distribution")
    plt.legend()
    plt.tight_layout()
    if output_path:
        plt.savefig(f"{output_path}_xz.png")
    if show:
        plt.show()
    plt.close()
    

def plot_2d(x, y, xlabel, ylabel, title, bins=(50, 50)):
    plt.hist2d(ak.to_numpy(x), ak.to_numpy(y), bins=bins)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.colorbar().ax.set_ylabel('# Entries')
    plt.tight_layout()
    plt.show()


