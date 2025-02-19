#!/bin/bash
#SBATCH --account=storm
#SBATCH --time=06:00:00
#SBATCH --job-name=Storm-batch-process
#SBATCH --nodes=1             # This should be nC/36 (36 cores on eagle)
#####SBATCH --ntasks-per-node=36
#SBATCH --mail-user mchetan@nrel.gov
#SBATCH --mail-type BEGIN,END,FAIL
#SBATCH --output=kestrel-logs/%j.%N.Storm-batch-process.log
###SBATCH --partition=debug

module purge

for mod in mamba git cmake craype-x86-spr intel-oneapi-compilers intel-oneapi-mpi intel-oneapi-mkl fftw/3.3.10-intel-oneapi-mpi-intel hdf5/1.14.1-2-intel-oneapi-mpi-intel netcdf-c/4.9.2-intel-oneapi-mpi-intel PrgEnv-intel
do
        echo "Loading $mod....."
        module load $mod
done

module unload gcc

# export OMP_NUM_THREADS=1

source activate /projects/storm/IdlingRotor/tools/env/storm-weis-kestrel-dev
which python
which ninja

echo $1

# ninja -j 103 -v -k 0 -f $1
python processingScript.py --path $1
