
# Functions for generating standard and custom plots for validation samples.


import matplotlib.pyplot as plt
import numpy as np
import awkward as ak
import os
import dask_awkward

def apply_root_style():
    plt.style.use("default")  # Reset to default style
    plt.rcParams.update({
        "font.family": "serif",  # Use serif font like ROOT
        "font.size": 20,         # Increase font size
        "axes.labelsize": 20,    # Axis label size
        "axes.titlesize": 22,    # Title size
        "xtick.labelsize": 14,   # X-axis tick size
        "ytick.labelsize": 14,   # Y-axis tick size
        "grid.color": "gray",    # Grid color
        "grid.linestyle": "--",  # Dashed grid lines
        "grid.linewidth": 0.5,   # Grid line width
        "axes.grid": True,       # Enable grid
        "axes.edgecolor": "black",  # Axis edge color
        "axes.linewidth": 1.2,      # Axis line width
        "legend.fontsize": 15,      # Legend font size
        "legend.frameon": False,    # Remove legend frame
    })
    
def plot_and_save_variable(array, var_name, sample_name, detector,
                           bins=50, ax=None, xlabel=None, ylabel="# Entries", yscale='linear', cut_applied=False, outdir=None, label='', **kwargs):
    """
    Plot a 1D histogram for `array`. Behavior:
      - If `ax` is None: create a new figure/axes, save (if outdir) and close the figure.
      - If `ax` is provided: draw on the provided axes and DO NOT close/clear it (caller manages final saving).
    Parameters:
      - array: data array to plot (numpy/awkward/dask-awkward)
      - var_name: variable name 
      - sample_name: sample identifier
      - detector: detector name 
      - bins: number of bins or bin edges
      - ax: matplotlib Axes to draw on (if None, create new)
      - xlabel: label for x-axis (if None, use var_name)
      - ylabel: label for y-axis
      - yscale: scale for y-axis ('linear' or 'log')
      - cut_applied: whether a cut was applied
      - outdir: output directory to save plot (if None, do not save)
      - label: legend label for the dataset
      - **kwargs: additional keyword arguments for future extensions
    """
    created_fig = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
        apply_root_style()
        created_fig = True
    else:
        fig = ax.get_figure()

    # ensure numpy array for hist plotting
    try:
        data = np.asarray(array)
    except Exception:
        data = array

    ax.hist(data, bins=bins, histtype='step', label=label, **kwargs)
    cut_str = " (cut applied)" if cut_applied else ""
    
    save_path = f"{detector}_{sample_name}_{var_name}_{cut_str}"
   
    ax.set_xlabel(xlabel if xlabel else var_name)
    ax.set_ylabel(ylabel)
    ax.set_yscale(yscale)
    plt.tight_layout()

    if outdir and created_fig:
        os.makedirs(outdir, exist_ok=True)
        save_path = os.path.join(outdir, save_path + ".png")
        fig.savefig(save_path)

    # Clean up: close figs we created. If caller provided ax, leave it intact for overlays/combined saving.
    if created_fig:
        plt.close(fig)

def plot_1d(array, xlabel, variable='energy', cut=None, ylabel="# Entries", ax=None, color='blue', title=None, bins=50, output_path=None, show=True):
    if type(array)==dask_awkward.lib.core.Array:
        data = array[variable].compute()
    else:
        data = array[variable]
    if cut is not None:
        data = data[cut]  
    plt.hist(data, bins=bins, histtype="step", color=color, linewidth=1.5)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    if title:
        plt.title(title)
    if output_path:
        plt.savefig(output_path)
    if show:
        plt.show()
    
    
def plot_2d(x, y, xlabel="x", ylabel="y", title=None, sample_name='', detector='', bins=(50,50), cmap='viridis', outdir=None, show=True):
    import matplotlib.pyplot as plt
    import numpy as np

    # ensure plain numpy arrays (works with awkward arrays too)
    x = np.asarray(x)
    y = np.asarray(y)

    fig, ax = plt.subplots(figsize=(7, 6))
    
    H, xedges, yedges, im = ax.hist2d(x, y, bins=bins, cmap=cmap)
    cbar = fig.colorbar(im, ax=ax)   

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if title is None:
        title = f"{detector} {sample_name} {xlabel} vs {ylabel}"
    
    save_path = title.replace(" ", "_")
    
    if title:
        ax.set_title(title)

    if outdir:
        os.makedirs(outdir, exist_ok=True)
        save_path = os.path.join(outdir, save_path+".png")
        plt.savefig(save_path)
        plt.close()
    if show:
        plt.show()
    else:
        plt.close(fig)

