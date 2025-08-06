import concurrent.futures
import os
import subprocess
import shutil



########### CHANGE THIS TO YOUR LOCAL DIRECTORY #############
d0z0_path = "/home/submit/escaso/summer2025/d0z0"
ceph_path = "/ceph/submit/data/user/e/escaso/FCC/summer2025/d0z0_results"
input_path = os.path.join(d0z0_path, "gun_input")
hepmc_path = os.path.join(d0z0_path, "gun_hepmc")

pdg_dict = {
    # Quarks
    1: "d",       -1: "d_bar",
    2: "u",       -2: "u_bar",
    3: "s",       -3: "s_bar",
    4: "c",       -4: "c_bar",
    5: "b",       -5: "b_bar",
    6: "t",       -6: "t_bar",
    7: "b'",      -7: "b'_bar",
    8: "t'",      -8: "t'_bar",

    # Leptons
    11:  "e_minus",       -11: "e_plus",
    12:  "nu_minus",      -12: "nu_e_bar",
    13:  "mu_minus",      -13: "mu_plus",
    14:  "nu_mu",     -14: "nu_mu_bar",
    15:  "tau_minus",     -15: "tau_plus",
    16:  "nu_tau",    -16: "nu_tau_bar",
    17:  "tau'_minus",    -17: "tau'_plus",
    18:  "nu_tau'",   -18: "nu_tau'_bar",
}


class Gun_directories:

    def __init__(self, detector):
        self.root = os.path.join(ceph_path, detector, f"gun_root")
        self.analysis = os.path.join(ceph_path, detector, f"gun_analysis")
        self.d0_plots = os.path.join(d0z0_path, detector, f"gun_d0_plots")
        self.z0_plots = os.path.join(d0z0_path, detector, f"gun_z0_plots")

    def create_directories(self):
        for path in [self.root, self.analysis, self.d0_plots, self.z0_plots]:
            os.makedirs(path, exist_ok=True)

### GENERATE DETECTOR RESPONSE ###
def detector_response(root_dir, detector_card, hepmcs_directory, max_workers = 12):

    def helper_response(hepmc):

        filename, _ = os.path.splitext(hepmc)

        command = (
            f"source {d0z0_path}/particleGun/env.sh && "
            "DelphesHepMC_EDM4HEP "
            f"{detector_card} "
            f"{d0z0_path}/delphes/cards/output.tcl "
            f"{root_dir}/{filename}.root "
            f"{hepmcs_directory}/{hepmc}"
        )

        subprocess.run(["bash", "-lc", command], check=True)

    # run response for each sample
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        for gun_hepmc in os.listdir(hepmcs_directory):
            pool.submit(helper_response, gun_hepmc)

 
### ANALYZE RESULTS ###
def analyze_trk(roots_directory, analysis_directory, analysis_filename = f"{d0z0_path}/delphes/analysis_trk.py", max_workers = 12):

    def helper_analyze(sample_name):
        print(f"Running {analysis_filename} on {sample_name}")

        command = (
            "source /work/submit/jaeyserm/software/FCCAnalyses/setup.sh && "
            f"python {analysis_filename} "
            f"--input {roots_directory}/{sample_name} "
            f"--output {analysis_directory}/{sample_name}"
        )

        subprocess.run(["bash", "-lc", command], check=True)


    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        for sample_name in os.listdir(roots_directory):
            pool.submit(helper_analyze, sample_name)


### PLOT RESULTS ###
def plot_d0z0(input_dir, d0_dir, z0_dir, gun_analysis_directory, subsystem, layer, radius, plot_filename = f"{d0z0_path}/delphes/plot_d0z0.py", max_workers = 12):
            
    def helper_plot(sample_name):

        name_no_ext = os.path.splitext(sample_name)[0]

        for hist_name, hist_abrev, output_dir in zip(["RP_TRK_D0_um", "RP_TRK_Z0_um"],["d0", "z0"], [d0_dir, z0_dir]):

            command = (
                "source /work/submit/jaeyserm/software/FCCAnalyses/setup.sh && "
                f"python {plot_filename} "
                f"--input {gun_analysis_directory}/{sample_name} "
                f"--output {output_dir}/{name_no_ext} "
                f"--inputCard {input_dir}/{name_no_ext}.input "
                f"--histName {hist_name} "
                f"--histAbreviation {hist_abrev} "
                f"--subsystem {subsystem} "
                f"--layer {layer} "
                f"--radius {radius} "
            )

            subprocess.run(["bash", "-lc", command], check=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        for sample_name in os.listdir(gun_analysis_directory):
            pool.submit(helper_plot, sample_name)

if __name__ == "__main__":
        
    #######################################
    # OPTION #1: WILL NOT RUN r_vs_res.py #
    #######################################
    # optimization_config = "inside_pipe"
    #
    # for detector in ["IDEA_base25", "IDEA_inside_10","IDEA_inside_10_original_wmb"]:
    #
    #     subsystem = "inside_pipe"
    #     layer = -1
    #     radius = -1
    #
    #######################################


    #########################################
    # OPTION #2: WILL RUN r_vs_res.py AFTER #
    #########################################

    optimization_config = "VTXIB_r1"
    
    for detector, radius in zip(["IDEA_VTXIB_r1_117", "IDEA_base25", "IDEA_VTXIB_r1_157"], [11.7, 13.7, 15.7]):
    
        subsystem = "VTXIB"
        layer = 1 # because r1 means first radius, aka the first layer of the vertex inner barrel

        detector_card = f"{d0z0_path}/delphes/cards/{detector}.tcl"
        detector_path = os.path.join(d0z0_path, optimization_config, detector)
        os.makedirs(detector_path, exist_ok=True)

        gun_dirs = Gun_directories(os.path.join(optimization_config, detector))
        gun_dirs.create_directories()

        detector_response(root_dir=gun_dirs.root, detector_card=detector_card, hepmcs_directory=hepmc_path)
        analyze_trk(roots_directory=gun_dirs.root, analysis_directory=gun_dirs.analysis)
        plot_d0z0(input_dir=input_path, d0_dir=gun_dirs.d0_plots, z0_dir=gun_dirs.z0_plots , gun_analysis_directory=gun_dirs.analysis,
                  subsystem=subsystem, layer=layer, radius=radius)
        