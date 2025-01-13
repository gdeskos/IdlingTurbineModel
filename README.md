## Dependancies

0. Clone this repo & checkout required branch
1. Load the required modules with:

        source kestrel-idling.sh    
        # ignore if env not found, we'll set it up next

2. Create Conda environment using `environment.yml` file

        conda config --add channels conda-forge
        conda install git

        conda env create --name weis-env -f environment.yml

    OR, use the below command to create a path specific conda env (Prefered)

        conda env create -p /path/to/new/env -f environment.yml
        

3. OpenFAST: https://github.com/mayankchetan/openfast/tree/of_io_tightCoupling

    - Building OpenFAST

            git clone https://github.com/mayankchetan/openfast
            cd openfast
            git checkout f_io_tightCoupling
            mkdir build
            cd build
            cmake ..
            make -j 4 openfast turbsim

    - Installing `openfast_io`

            cd ..
            cd openfast_io
            pip install -e .


## Running the model

0. Do not run this on Kestrel login nodes, get a single compute node.

1. Load modules and activate env
    - replace `your_env_name` in the `kestrel-idling.sh` to point to env from previous step
    - Assuming a new shell:

            source kestrel-idling.sh

    - if env is not loaded then:
            
            conda activate <<path to env created>>

1. Generating wind inputs:

    - Open `scipts/rampedTurbulance.ipynb`
    - Set values for 
        - `hurrCat` for the Hurricane category
        - `numSeeds` for the number of seeds to genearate
        - `writeFolder` location to write the TurbSim files to
        - `baseInputFolder` location of the refernce folder
        - `TurbSimExe` path to turbsim executable from previous step
    - Run the notebook (takes ~45min)

2. Generating the OpenFAST files:
    - Edit `scripts/TurbRuns.py`
        - `TMax` for simulation runtime
        - `runDir` path to where you want the OpenFAST cases to be generated.
        - `WindInputFolder` path to wind input files
        - `workingFilePrefix` prefix for all the newly written OpenFAST files
        - `UAmodel` UA model to use -->  0=Quasi-steady (no UA), 2=B-L Gonzalez, 3=B-L Minnema/Pierce, 4=B-L HGM 4-states, 5=B-L HGM+vortex 5 states, 6=Oye, 7=Boeing-Vertol
        - `DLC` Name of the DLC
        - `fastEXE` path to openfast executable from previous step

    - Run the script using:

            cd scripts
            python TurbRuns.py

3. Setting up for bulk Kestrel runs:
    - Change directory to `runDir`:
    - Edit `a_ninjaWriter_number-multiSbash.sh` file in the `runDir` folder.
    - on line `21` replace `"./unsteady/*.fst"` to point to the folder where the input files are, you can get creative with this. Always end with `/*.fst`.
    - on line `31` replace `/projects/bar/mchetan/tools/openfast/tightCoupling-mc-FullUA/build/glue-codes/openfast/openfast` with the absolute path to the OpenFAST exe.
    - run the scipt using:

            bash a_ninjaWriter_number-multiSbash.sh

4. Finally running it!
    - One folder `aa_ninjaFiles` and one file `a_serial.sh` will be generated from `Step 3`
    - Edit the SBATCH directives in `Submit-serial.sh` with your credentials 
    - Once all the details are verified, you are ready to set the Kestrel runs.
    - `NOTE: The next step will spin up multiple single node jobs, please be sure before executing`
    - Start all runs:
    
                bash a_serial.sh


