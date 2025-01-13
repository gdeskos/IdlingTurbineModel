#!/bin/bash

# Verify we're on Kestrel
if [[ ! "$NREL_CLUSTER" =~ "kestrel" ]]; then
    echo "Error: This script must be run on Kestrel"
    exit 1
fi

# Load required modules
echo " "
echo "Loading modules for Kestrel login node $HOSTNAME...."

module purge

for mod in mamba git cmake craype-x86-spr intel-oneapi-compilers intel-oneapi-mpi intel-oneapi-mkl fftw/3.3.10-intel-oneapi-mpi-intel hdf5/1.14.1-2-intel-oneapi-mpi-intel netcdf-c/4.9.2-intel-oneapi-mpi-intel PrgEnv-intel
do
        echo "Loading $mod....."
        module load $mod
done

echo "Unloading GCC...."
module unload gcc

# Activate conda environment (replace 'your_env_name' with actual environment name)
eval "$(conda shell.bash hook)"
conda activate your_env_name

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate conda environment"
    # exit 1
fi

echo "Environment successfully set up on Kestrel"

