## Dependancies

0. Clone this repo & checkout required branch
1. Load the required modules with:

        source kestrel-idling.sh    
        # ignore if env not found, we'll set it up next

2. Create Conda environment using `environment.yml` file

        conda config --add channels conda-forge
        conda install git

        conda env create --name weis-env -f environment.yml
        

3. OpenFAST: https://github.com/mayankchetan/openfast/tree/of_io_tightCoupling

    - Building OpenFAST

            git clone https://github.com/mayankchetan/openfast
            cd openfast
            git checkout f_io_tightCoupling
            mkdir build
            cd build
            cmake ..
            make -j 4 openfast

    - Installing `openfast_io`

            cd ..
            cd openfast_io
            pip install -e .

