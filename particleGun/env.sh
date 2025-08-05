source /cvmfs/sw.hsf.org/key4hep/setup.sh -r 2023-11-23

cd /home/submit/escaso/summer2025/d0z0/k4SimDelphes/install
export PATH=$(pwd)/bin:${PATH}
export LD_LIBRARY_PATH=$(pwd)/lib64:${LD_LIBRARY_PATH}
cd /home/submit/escaso/summer2025/d0z0/particleGun