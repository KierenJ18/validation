# statistical_test_uniform_minimal.py
from scipy.stats import kstest, chisquare, norm
from data_loading import load_validation_data, return_parent_params
import numpy as np
import matplotlib.pyplot as plt
import warnings
import os

# --- Load data ---
directory = "/vols/hyperk/users/kj4718/validation/analysed_results/IWCD/id_elneg/wcsimrootevent"
per_event, per_trigger, per_file = load_validation_data(directory, max_files=10)
energy = return_parent_params(per_event, detector="IWCD")["energy"]

# --- Utilities ---
def scale_to_unit(data, eps=1e-10):
    """Safely scale numeric array to (0,1), avoiding exact 0 or 1."""
    a = np.asarray(data, dtype=float)
    # handle degenerate case
    if np.nanmax(a) == np.nanmin(a):
        return np.full_like(a, 0.5)
    scaled = (a - np.nanmin(a)) / (np.nanmax(a) - np.nanmin(a))
    return np.clip(scaled, eps, 1 - eps)

def p_to_sigma(p, two_sided=True, cap=9.0):
    """
    Convert p-value to sigma (Gaussian stddevs).
      - For two-sided tests set two_sided=True (use p/2).
      - For one-sided tail p set two_sided=False (use p directly).
    cap: maximum sigma to return for display (prevents astronomically large numbers).
    """
    if p <= 0:
        return float("inf")
    tail = (p / 2.0) if two_sided else p
    # isf returns z such that P(Z > z) = tail
    z = norm.isf(tail)
    if np.isinf(z) or np.isnan(z):
        return float("inf")
    return min(z, cap)

def fmt_p_sigma(p, sigma):
    if np.isinf(sigma):
        return f"p = {p:.3e}, σ > {9}"
    else:
        return f"p = {p:.4f}, σ = {sigma:.3f}"

# --- Prepare data ---
energy_scaled = scale_to_unit(energy)

# --- Run tests ---
ks_stat, ks_p = kstest(energy_scaled, "uniform")
counts, _ = np.histogram(energy_scaled, bins=100)  # you may change bins
chi2_stat, chi2_p = chisquare(counts)  # default expected = uniform counts

# Convert p-values to sigma
ks_sigma = p_to_sigma(ks_p, two_sided=True)       # KS is interpreted two-sided
chi2_sigma = p_to_sigma(chi2_p, two_sided=False)  # Chi-square p is an upper-tail probability

# --- Print results ---
print("\nUniformity tests (data scaled to (0,1))")
print("------------------------------------------------")
print(f"KS test:   statistic = {ks_stat:.6f}, {fmt_p_sigma(ks_p, ks_sigma)} (two-sided)")
print(f"Chi² test: statistic = {chi2_stat:.6f}, {fmt_p_sigma(chi2_p, chi2_sigma)} (one-sided)")
print("------------------------------------------------\n")

# Simple interpretation
if ks_p < 0.05 or chi2_p < 0.05:
    warnings.warn("Data shows statistically significant deviation from uniformity (p < 0.05).")
else:
    print("Data does not show statistically significant deviation from uniformity (p >= 0.05).")

# --- Plots (Q-Q vs Uniform and histogram) ---
os.makedirs("plots", exist_ok=True)

# Q-Q plot for Uniform(0,1)
data_sorted = np.sort(energy_scaled)
theoretical = np.linspace(0, 1, len(data_sorted), endpoint=False) + 0.5/len(data_sorted)
plt.figure(figsize=(5,5))
plt.scatter(theoretical, data_sorted, s=8, alpha=0.6)
plt.plot([0,1],[0,1], "r--")
plt.xlabel("Theoretical quantiles (Uniform[0,1])")
plt.ylabel("Sample quantiles")
plt.title("Q–Q vs Uniform(0,1)")
plt.axis("square")
qqfile = os.path.join("plots", "qqplot_uniform.png")
plt.tight_layout()
plt.savefig(qqfile)
plt.show()

# Histogram
plt.figure(figsize=(6,4))
plt.hist(energy_scaled, bins=50, density=True, alpha=0.7)
plt.axhline(1, color="red", linestyle="--", label="Ideal uniform density")
plt.xlabel("Scaled value")
plt.ylabel("Density")
plt.title("Histogram of scaled data")
plt.legend()
histfile = os.path.join("plots", "histogram_uniform.png")
plt.tight_layout()
plt.savefig(histfile)
plt.show()

print(f"Saved plots to: {qqfile}, {histfile}\n")
