import os
import numpy as np
import matplotlib.pyplot as plt

d0z0_path = "/home/submit/escaso/summer2025/d0z0"

detector_names = [
    # "CLD_2T",
    # "IDEA_2T",
    # "IDEA_3T",
    # "CLD_3T",
    # "CLD_2T_117_200_315",
    # "CLD_2T_120_200_315",
    # "CLD_2T_80_200_315",
    # "CLD_2T_190_200_315",
    "IDEA_2T_117_200_315",
    "IDEA_2T_137_200_315",
    "IDEA_2T_190_200_315",
]

ratio_pairs = [
    # ("CLD_3T", "CLD_2T"), # CLD_3T/CLD_2T
    # ("IDEA_3T", "IDEA_2T"),
    # ("CLD_2T_117_200_315", "CLD_2T_120_200_315"),
    # ("CLD_2T_120_200_315", "CLD_2T_80_200_315"),
    # ("CLD_2T_117_200_315", "CLD_2T_190_200_315")
    ("IDEA_2T_117_200_315", "IDEA_2T_137_200_315"),
    ("IDEA_2T_117_200_315", "IDEA_2T_190_200_315"),
]

THETA = 0
SIGMA = 1

momentum_ranges = [1, 5, 10, 50, 100]
colors  = ['k','r','b','g','m']
markers = ['o','s','^','d','v']

momentum_markers = {mom: (c,m) for mom,c,m in zip(momentum_ranges, colors, markers)}

# Store all sigma data for later ratio plotting 
all_data = {"d0": {}, "z0": {}}

for param in ["d0", "z0"]:
    all_data[param] = {}  # Reset for each param

    for detector in detector_names:
        fig, ax = plt.subplots(figsize=(6,5))  # One plot per detector

        detector_path = os.path.join(d0z0_path, detector)
        detector_label = detector.replace("_", " ")

        theta_dict = {p: [] for p in momentum_ranges}
        sigma_dict = {p: [] for p in momentum_ranges}
        all_data[param][detector] = (theta_dict, sigma_dict)

        input_dir = os.path.join(detector_path, f"gun_{param}_plots")

        for filename in os.listdir(input_dir):
            _, _, _, theta, _, p, _, sigma = os.path.splitext(filename)[0].split("_")
            p = int(p)
            theta = float(theta)
            sigma = float(sigma)

            # Store in all_data for later use
            all_data[param][detector][THETA][p].append(theta)
            all_data[param][detector][SIGMA][p].append(sigma)            

        for p in momentum_ranges:
            # sort them in case the filenames are not sorted
            theta_arr, sigma_arr = zip(*sorted(zip(all_data[param][detector][0][p], all_data[param][detector][1][p])))
            color, marker = momentum_markers[p]
            ax.plot(theta_arr, sigma_arr, label=f"p = {p} GeV", color=color, marker=marker, linestyle='-')

        ax.set_xlabel(r"$\theta$ [deg]", ha='right', x=1.0)
        ax.set_ylabel(rf"$\sigma(\Delta {param}_0)$ [$\mu$m]")
        ax.set_yscale("log")
        ax.grid(True, linestyle='--', linewidth=0.5)
        ax.legend(loc='upper right', fontsize=9)

        fig.suptitle(f"{param.upper()} resolution vs $\\theta$", fontsize=16)
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        save_path = f"{d0z0_path}/{param}_plots"
        os.makedirs(save_path, exist_ok=True)

        fig.savefig(f"{save_path}/{param}_{detector}.png")
        fig.savefig(f"{save_path}/{param}_{detector}.pdf")
        plt.close(fig)

    # --- Plot 3T / 2T Ratios using `all_data` ---
    for pair in ratio_pairs:
        fig, ax = plt.subplots(figsize=(6, 4))

        for p in momentum_ranges:
            theta_vals = all_data[param][pair[0]][THETA][p]
            sigma_numerator = np.array(all_data[param][pair[0]][SIGMA][p])
            sigma_denominator = np.array(all_data[param][pair[1]][SIGMA][p])

            ratio = sigma_numerator / sigma_denominator # because ratio is a division of np.arrays, 
            color, marker = momentum_markers[p]
            ax.plot(theta_vals, ratio, label=f'p = {p} GeV', color=color, marker=marker)

        ax.axhline(1.0, color='gray', linestyle='--', linewidth=1)
        ax.set_ylim(0.8, 1.4)
        ax.set_xlabel(r"$\theta$ [deg]", ha='right', x=1.0)
        ax.set_ylabel(f"{pair[0]} / {pair[1]} ratio")
        ax.set_title(f"{pair[0]} / {pair[1]}: {param.upper()} resolution ratio", fontsize=14)
        ax.grid(True, linestyle='--', linewidth=0.5)
        ax.legend(loc='upper right', fontsize=9)

        plt.tight_layout()
        fig.savefig(f"{d0z0_path}/{param}_plots/{param}_{pair[0]}_{pair[1]}_ratio.png")
        fig.savefig(f"{d0z0_path}/{param}_plots/{param}_{pair[0]}_{pair[1]}_ratio.pdf")
        plt.close(fig)
