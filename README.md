# d0 and z0 analysis
The files in this directory provide the tools for a d0 and z0 analysis of particle guns in Delphes.

Start by `ssh`-ing, but do not `source` yet. Before running these files, you will have to make some changes in terms of directory paths.

## `gun.py`
`gun.py` generates input gun samples and runs the HEPMC3 gun on them. As it is right now, `gun.py` is formatted to produce a single particle muon gun at different theta ranges and run these guns on different momentum ranges. Consequently, adjust the following parameters:
  - Below the imports section:
    - set `d0z0_path` to be the global path to the directory that was created by cloning this repository.
  - In `__main__`:
    - `theta_ranges`: These are the theta values at which the single particle gun will be shot at.
    - `mom_ranges`: These are the momentum values which the particles will move at.
    - `particle_id`: Select which particle you want to shoot. In this case, `13` is for anti-muon. You can find a pdg dictionary at the top of the file.
    - `nevents`: Number of events generated per theta value, per momentum value.
    - `npart`: Number of particles contained in each event.
      
## `d0z0.py`
