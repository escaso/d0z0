import concurrent.futures
import os
import subprocess

d0z0_path = "/home/submit/escaso/summer2025/d0z0"


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
    14:  "nu_mu",         -14: "nu_mu_bar",
    15:  "tau_minus",     -15: "tau_plus",
    16:  "nu_tau",        -16: "nu_tau_bar",
    17:  "tau'_minus",    -17: "tau'_plus",
    18:  "nu_tau'",       -18: "nu_tau'_bar",
}

### GENERATE INPUT GUN SAMPLES ###
def generate_samples(input_dir, theta_range, mom_range, pid, nevents = 100000, npart = 1, max_workers = 12):
    
    def helper_ranges():
        for theta in theta_range:
            for mom in mom_range:
                yield theta, mom

    def helper_write(theta, mom):

        filename = os.path.join(input_dir, f"{pdg_dict[pid]}_theta_{theta}_p_{mom}.input")
        
        with open(filename, 'w') as f:
            f.write(f"npart {npart}\n")
            f.write(f"theta_range {theta}.0,{theta}.0\n")
            f.write(f"mom_range {mom}.0,{mom}.0\n")
            f.write(f"pid_list {pid}\n")
            f.write(f"nevents {nevents}\n")

        print(f"Generated {filename}")

    print("Starting gun generator")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        for theta, mom in helper_ranges():

            # submit’s signature is: submit(fn, *args, **kwargs), so it knows that theta and mom are arguments
            pool.submit(helper_write, theta, mom)

    print("All tasks complete")


### RUN GUN ON SAMPLES ###
def run_samples(samples_directory, hepmcs_directory, gun_path = f"{d0z0_path}/particleGun/run_gunHEPMC3_singularity.sh", max_workers = 12):

    path_to_gunHEPMC3 = f"{d0z0_path}/particleGun/gunHEPMC3"

    def helper_run(input_path):
        """
        $1: directory to cd into (where you want to run the command, so output files go there)
        $2: command to run (./gunHEPMC3)
        $3: argument to that command (input file)
        $4: directory to cd back to (starting directory)
        """
        try:

            subprocess.run([
                gun_path, 
                hepmcs_directory,
                path_to_gunHEPMC3,
                input_path,
                d0z0_path
            ], check=True)
            print("Processed", input_path)
        
        except Exception as e:
            print(f"Unknown error for {input_path}: {e}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        for sample_name in os.listdir(samples_directory):
            pool.submit(helper_run, os.path.join(samples_directory, sample_name))

if __name__ == "__main__":

    input_path = os.path.join(d0z0_path, "gun_input")
    hepmc_path = os.path.join(d0z0_path, "gun_hepmc")

    os.makedirs(input_path, exist_ok=True)
    os.makedirs(hepmc_path, exist_ok=True)

    theta_ranges = [10, 20, 30, 40, 50, 60, 70, 80, 90]
    mom_ranges = [1, 5, 10, 50, 100]
    particle_id = 13
    nevents = 100000
    npart = 1

    generate_samples(input_dir=input_path, theta_range=theta_ranges, mom_range=mom_ranges, pid=particle_id, nevents=nevents, npart=npart)
    run_samples(samples_directory=input_path, hepmcs_directory=hepmc_path)
