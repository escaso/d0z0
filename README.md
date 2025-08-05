# d0 and z0 analysis
The files in this directory provide the tools for a d0 and z0 analysis of particle guns in Delphes.

## `gun.py`
`gun.py` generates input gun samples and runs the HEPMC3 gun on them. As it is right now, `gun.py` is formatted to produce a single particle muon gun at different theta ranges and run these guns on different momentum ranges. Consequently, adjust the following parameters:
- Below the imports section:
  - Set `d0z0_path` to be the global path to the directory that was created by cloning this repository.
- In `__main__`:
  - `theta_ranges`: These are the theta values at which the single particle gun will be shot at.
  - `mom_ranges`: These are the momentum values which the particles will move at.
  - `particle_id`: Select which particle you want to shoot. In this case, `13` is for anti-muon. You can find a pdg dictionary at the top of the file.
  - `nevents`: Number of events generated per theta value, per momentum value.
  - `npart`: Number of particles contained in each event.
      
## `d0z0.py`
`d0z0.py` generates the detector response to these events, analyzes the results, and plots this analysis. To be adjusted:
- Below the imports section:
  - Again, set `d0z0_path` to be the global path to the directory that was created by cloning this repository.
  - Also set `ceph_path` to be the global path to your ceph directory, or any other directory with sufficient storage for the files created. It is computationally cheaper to store these files rather than recreate them each time.
- In `__main__`:
  - If you are running different iterations of the same geometry configuration but changing only one parameter, you can set the name of the parameter in `subsystem` (string), the layer you are changing in `layer` (int) and its value in `radius` (float). These parameters are necessary when planning to run `r_vs_res.py` but unnecessary otherwise.
    - For example, if you want to study the relationship of the first layer of the IDEA vertex detector inner barrel layer 1 and the d0/z0 resolution, the `subsystem` will be `"VTXIB"`, the `layer` will be `1`, and the `radius` will be `11.7`, `13.7`, `15.7`, etc.
  - Alternatively, if you will not be running `r_vs_res.py`, you can leave `layer = -1` and `radius = -1`. You can still take advantage of the `.json` file created by specifying what kind of analysis you are performing in `subsystem`. For example, `"long_barrel"`, `"short_barrel"`, etc.

## `plot_ratios.py`
`plot_ratios.py` plots both the individual d0/z0 resolution vs. the different theta values from your `theta_ranges` and the resolution ratio against your default detector (normally `IDEA_base25`).
- In `__main__`:
  - Set `d0z0_path` to be the global path to the directory that was created by cloning this repository.
  - Set the parameter occupied by `"inside_pipe"` in `detector_path = os.path.join(d0z0_path, "inside_pipe")` to be the name of the folder inside your `d0z0_path` that holds your analysis files. The idea is to have different folders for different kinds of studies, e.g. `"long_barrel"`, `"short_barrel"`.

## `r_vs_res.py`
`r_vs_res.py` plots both the individual d0/z0 resolution vs. the different theta values from your `theta_ranges` and the resolution ratio against your default detector (normally `IDEA_base25`).
- In `__main__`:
  - Set `d0z0_path` to be the global path to the directory that was created by cloning this repository.
  - Set the parameter occupied by `"inside_pipe"` in `detector_path = os.path.join(d0z0_path, "inside_pipe")` to be the name of the folder inside your `d0z0_path` that holds your analysis files. The idea is to have different folders for different kinds of studies, e.g. `"long_barrel"`, `"short_barrel"`.

## `delphes/cards`
`delphes/cards` is where your detector cards are stored.

## RUNNING THE ANALYSIS

1.Start by `ssh`-ing, **but do not `source` yet**. Before running these files, you will have to make some changes in terms of directory paths.

2.Make the necessary changes to `gun.py`. Then,

```bash
python gun.py```

3.Add whatever cards you will run on to `delphes/cards`.

4.Make the necessary changes to `d0z0.py`. Then,
```bash
python d0z0.py```

5.Now, `source` before running `plot_ratios.py` and/or `r_vs_res.py`.  
```bash
source /cvmfs/sw.hsf.org/key4hep/setup.sh -r 2025-05-29
python plot_ratios.py -d IDEA_VTXIB_r1_117 IDEA_VTXIB_r1_157 -p res_quantile
```
  -Note: Possible arguments for `-p`, which specifies the resolution parameter to be plotted, will be displayed if you run 
```bash
python plot_ratios.py -dis```
  -Optional: 
```bash
source /cvmfs/sw.hsf.org/key4hep/setup.sh -r 2025-05-29
python r_vs_res.py -d IDEA_VTXIB_r1_117 IDEA_VTXIB_r1_157 -p res_quantile
```

