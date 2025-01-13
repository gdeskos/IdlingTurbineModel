from util.runFAST_pywrapper import runFAST_pywrapper_batch
from util.CaseGen_General import CaseGen_General
from openfast_io.turbsim_util import TurbsimReader, TurbsimWriter
import numpy as np
import os
import pickle
import shutil

import matplotlib.pyplot as plt
from sys import platform

import argparse

try:
    if os.environ['NREL_CLUSTER'] == 'kestrel':
        kestrelFlag = True
    else:
        kestrelFlag = False
except KeyError:
    kestrelFlag = False

# # Initialize parser
parser = argparse.ArgumentParser()

# # Adding optional argument
parser.add_argument("--numCores", type = int, help = "Number of cores to use", default=1)

# # Read arguments from command line
args = parser.parse_args()



### Simulation settings
TMax = 1120.  # Length of wind grids and OpenFAST simulations, suggested 720 s
runDir = os.path.join(f'/scratch/{os.environ['USER']}/idlingRotor/','CAT2')
WindInputFolder = '../turb_sim/TurbSimGenFiles/CAT2'            # will read in all .bts files in this folder
workingFilePrefix = 'stormDlcs'                                 # Prefix for the working files  

UAmodel = 4 # 0=Quasi-steady (no UA), 2=B-L Gonzalez, 3=B-L Minnema/Pierce, 4=B-L HGM 4-states, 5=B-L HGM+vortex 5 states, 6=Oye, 7=Boeing-Vertol

DLC = '6.1' # or '6.2'

fastEXE = '../../i_decFiles/openfast/build/glue-codes/openfast/openfast'  # Path to OpenFAST executable 

# Adv user settings
AeroDynFile = 'IEA-15-240-RWT-LandBased_AeroDyn15_cfd.dat' # for CFD polars, 'IEA-15-240-RWT-LandBased_AeroDyn15.dat' for stock polars



### Main function
def main():

    # Paths calling the standard modules of WEIS
    fastBatch = runFAST_pywrapper_batch()
    run_dir = os.path.dirname( os.path.realpath(__file__) ) + os.sep
    fastBatch.FAST_directory = os.path.join(run_dir, '../openfast_model')   # Path to fst directory files
    fastBatch.FAST_InputFile    = 'IEA-15-240-RWT-LandBased.fst'   # FAST input file (ext=.fst) # RAAW_unbalanced.fst for b1 + 3% mass increase


    fastBatch.FAST_runDirectory = os.path.join(runDir, 'unsteady' if UAmodel > 0 else 'steady') # Output directory
    fastBatch.debug_level       = 0
    # User settings
    n_cores     = args.numCores     # Number of available cores
    TStart      = 0. # Start of the recording of the channels of OpenFAST

    ##### Settings passed to OpenFAST main file
    case_inputs = {}
    case_inputs[("Fst","TMax")]             = {'vals':[TMax], 'group':0}
    case_inputs[("Fst","DT")]               = {'vals':[1 / 1000], 'group':0} # Time for BeamDyn
    case_inputs[("Fst","NumCrctn")]         = {'vals':[0], 'group':0} # Predictor-corrector flag
    case_inputs[("Fst","CompAero")]         = {'vals':[2], 'group':0}
    case_inputs[("Fst","CompElast")]        = {'vals':[2], 'group':0} # Turning on BeamDyn
    case_inputs[("Fst","CompInflow")]       = {'vals':[1], 'group':0}
    case_inputs[("Fst","DT_Out")]           = {'vals':[0.01], 'group':0}
    case_inputs[("Fst","OutFileFmt")]       = {'vals':[1], 'group':0}
    case_inputs[("Fst","SttsTime")]         = {'vals':[case_inputs[("Fst","DT_Out")]['vals'][0]*10], 'group':0}

    case_inputs[("Fst","AeroFile")]         = {'vals':[AeroDynFile], 'group':0} # Pointing to the polars without 3D corrections

    ##### Settings for AeroDyn
    case_inputs[("AeroDyn","Wake_Mod")]  = {'vals':[0], 'group':0}     # Turning off BEM/DBEM
    
    # If unsteady airfoil aerodynamics is used, then the following settings are needed
    case_inputs[("AeroDyn","UA_Mod")]      = {'vals':[UAmodel], 'group': 4} # get inout from User
    case_inputs[("AeroDyn","TwrPotent")]  = {'vals':[0], 'group':0}   # Turning off tower potential flow
    case_inputs[("AeroDyn","TwrShadow")]  = {'vals':[0], 'group':0}   # Turning off tower shadow


    ##### Settings for Structural/ElastoDyn & ServoDyn

    # Idling has no brake! 
    lastGroup = 5
    ####### Idling ONLY case #######
    case_inputs[("ElastoDyn","GenDOF")]     = {'vals':['True'], 'group':lastGroup} # True -> Idle, False -> Locked rotor
    case_inputs[("Fst","CompServo")]        = {'vals':[1], 'group':lastGroup} # Same as above
    case_inputs[("ServoDyn","PCMode")]      = {'vals':[0], 'group':lastGroup} # Same as above
    case_inputs[("ServoDyn","VSContrl")]    = {'vals':[0], 'group':lastGroup} # Same as above
    case_inputs[("ServoDyn","GenTiStr")]    = {'vals':['True'], 'group':lastGroup} # Same as above
    case_inputs[("ServoDyn","TimGenOn")]   = {'vals':[3000], 'group':lastGroup} # Same as above

    case_inputs[("ElastoDyn","BlPitch1")]   = {'vals': [90], 'group': 0}  # Pitching to feather
    case_inputs[("ElastoDyn","BlPitch2")]   = case_inputs[("ElastoDyn","BlPitch1")]  # Setting pitch angle; B1 to be used for offset.
    case_inputs[("ElastoDyn","BlPitch3")]   = case_inputs[("ElastoDyn","BlPitch2")]
    case_inputs[("ElastoDyn","Azimuth")]    = {'vals': [0], 'group': 2} # Relying on rotor symmetry, must be [0, 360) degrees); so 300, 330, 0, 30, 60
    case_inputs[("ElastoDyn","RotSpeed")]   = {'vals': [0], 'group': 0} # Setting to be stand-still

    # case_inputs[("ElastoDyn","NacYaw")]     = {'vals': np.linspace(-179,180,33), 'group': 3} # Yaw angles  np.linspace(-50,50,21)

    if DLC == '6.1':


        case_inputs[("ElastoDyn","NacYaw")]     = {'vals': np.array([-20., -15., -10.,  -5.,   0.,   5.,  10.,  15.,  20., # higher resolution between -20 and 20 deg
                                                                    ]), 'group': 3}
    elif DLC == '6.2':
    
        case_inputs[("ElastoDyn","NacYaw")]     = {'vals': np.array([-179., -165., -150., -135., -120., -105.,  -90.,  -75.,  -60., -45.,  -30., # 15 deg spec as per IEC
                                                                    -20., -15., -10.,  -5.,   0.,   5.,  10.,  15.,  20., # higher resolution between -20 and 20 deg
                                                                    30.,   45.,   60.,   75., 90.,  105.,  120.,  135.,  150.,  165.,  180.]), 'group': 3} # Yaw angles  np.linspace(-50,50,21)

    ##### Settings for Inflows!!

    # find the '.bts' files in the folder provided by the user
    turbFiles = [os.path.join(WindInputFolder, f) for f in os.listdir(WindInputFolder) if f.endswith('.bts')]
    turbFiles.sort()
    case_inputs[("InflowWind","WindType")]  = {'vals':[3], 'group':0}
    case_inputs[("InflowWind","FileName_BTS")]= {'vals': turbFiles, 'group': 1} # forcing WS

    # Handling the OpenFAST version, Not needed in this implimentation
    if kestrelFlag:
        dll = ["/usr/share/miniconda3/envs/test/lib/libdiscon.so"]
        fastBatch.FAST_exe = '/projects/bar/mchetan/tools/openfast/tightCoupling-mc/build/glue-codes/openfast/openfast'
        # fastBatch.FAST_exe = '/projects/storm/IdlingRotor/tools/openfast/of-v351/build/glue-codes/openfast/openfast'
    elif platform == 'darwin':
        dll = ["/Users/mchetan/Desktop/nrel/projects/bar/instability-raaw/numericalWork/rosco/rosco-mc-dev/ROSCO/build/libdiscon.dylib"]
        fastBatch.FAST_exe = '/Users/mchetan/Desktop/nrel/projects/bar/instability-raaw/numericalWork/openfast-v3-2'

    # Generate the matrix of cases
    case_list, case_name_list = CaseGen_General(case_inputs, dir_matrix=fastBatch.FAST_runDirectory, namebase=workingFilePrefix)

    fastBatch.case_list = case_list
    fastBatch.case_name_list = case_name_list
    fastBatch.use_exe = True
    fastBatch.allow_fails = True

    with open(f'{fastBatch.FAST_runDirectory}/case_inputs.pkl', 'wb') as handle:
        pickle.dump((case_inputs, fastBatch) , handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Run OpenFAST, either serially or sequentially
    if n_cores == 1:
        summary_stats, extreme_table, DELs, Damage, ct = fastBatch.run_serial()
    else:
        summary_stats, extreme_table, DELs, Damage, ct = fastBatch.run_multi(n_cores)


def copyNinjaRelatedFiles():
    # files to copy are a_ninjaWriter_number-multiSbash.sh, a_serial.bash, Submit-serial.sh
    # copy the files to the runDir
    shutil.copy2('a_ninjaWriter_number-multiSbash.sh', runDir)
    shutil.copy2('Submit-serial.sh', runDir)

    # print run instructions for the user
    print('************************************************************************')
    print('Follow the README instructions to run the simulations on kestrel nodes.')
    print('************************************************************************')


if __name__ == '__main__':
    main()
    copyNinjaRelatedFiles()