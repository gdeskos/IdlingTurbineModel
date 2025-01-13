#!/bin/bash

# Verify we're on Kestrel
if [[ ! $(NREL_CLUSTER) =~ "kestrel" ]]; then
    echo "Error: This script must be run on Kestrel"
    exit 1
fi

# Load required modules
module purge
module load python/3.9.12
module load conda/23.1.0

# Activate conda environment (replace 'your_env_name' with actual environment name)
eval "$(conda shell.bash hook)"
conda activate your_env_name

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate conda environment"
    exit 1
fi

echo "Environment successfully set up on Kestrel"