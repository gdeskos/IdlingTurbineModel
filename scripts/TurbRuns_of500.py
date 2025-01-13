from weis.aeroelasticse.runFAST_pywrapper import runFAST_pywrapper_batch
from weis.aeroelasticse.CaseGen_General import CaseGen_General
import numpy as np
import os
import pickle

import matplotlib.pyplot as plt
# from scipy.fft import fft, fftfreq
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
# # parser.add_argument("--startW", type = float, help = "Start Wind Speed")
# # parser.add_argument("--endW", type = float, help = "End Wind Speed")
parser.add_argument("--numCores", type = int, help = "Number of cores to use", default=1)

# # Read arguments from command line
args = parser.parse_args()

if __name__ == '__main__':

    # Paths calling the standard modules of WEIS
    fastBatch = runFAST_pywrapper_batch()
    run_dir = os.path.dirname( os.path.realpath(__file__) ) + os.sep
    fastBatch.FAST_directory = os.path.join(run_dir, '../OpenFAST','IEA-15-240-RWT-LandBased_of500')   # Path to fst directory files
    fastBatch.FAST_InputFile    = 'IEA-15-240-RWT-LandBased.fst'   # FAST input file (ext=.fst) # RAAW_unbalanced.fst for b1 + 3% mass increase
    # fastBatch.FAST_runDirectory = os.path.join(run_dir , '..', '..', 'outputs', 'tower-s2s-9P', '01_steady_BD_noBlUb_PF_sweep_7_14_G1022_17AUG')


    fastBatch.FAST_runDirectory = os.path.join('/scratch/mchetan/idlingRotor/paper/tight-coupling', # 'steady-af-steady', 'steady-af-unsteady', 
                                                'of500' ,'steady')


    fastBatch.debug_level       = 0

    # User settings
    n_cores     = args.numCores     # Number of available cores
    TMax        = 1120.  # Length of wind grids and OpenFAST simulations, suggested 720 s

    # flex = np.loadtxt(os.path.join(run_dir, '../../raaw-turb', 'Turbine Data', 'FLEX_MODEL','StartPar_127.tab'), skiprows=55)
    # wind_speeds = list(np.linspace(7,14,8))#[12.75] # Rated wind condition?
    TStart      = 0. # Start of the recording of the channels of OpenFAST

    # Settings passed to OpenFAST
    case_inputs = {}
    case_inputs[("Fst","TMax")]             = {'vals':[TMax], 'group':0}
    case_inputs[("Fst","DT")]               = {'vals':[1 / 1000], 'group':0} # Time for BeamDyn
    case_inputs[("Fst","TMax")]             = case_inputs[("Fst","DT")]
    case_inputs[("Fst","NumCrctn")]         = {'vals':[0], 'group':0} # Predictor-corrector flag



    case_inputs[("Fst","CompAero")]         = {'vals':[2], 'group':0}
    case_inputs[("Fst","CompElast")]        = {'vals':[2], 'group':0} # Turning on BeamDyn
    case_inputs[("Fst","CompInflow")]       = {'vals':[1], 'group':0}

    # case_inputs[("Fst","AirDens")]        = {'vals':[1.05], 'group':0} # Might be intersting to see the effect of density loads

    case_inputs[("Fst","DT_Out")]           = {'vals':[0.01], 'group':0}
    case_inputs[("Fst","OutFileFmt")]           = {'vals':[1], 'group':0}

    case_inputs[("Fst","SttsTime")]         = {'vals':[case_inputs[("Fst","DT_Out")]['vals'][0]*10], 'group':0}

    # case_inputs[("Fst","AeroFile")]         = {'vals':['IEA-15-240-RWT_Land-Based_AeroDyn15_no3D.dat'], 'group':0} # Pointing to the polars without 3D corrections

    ##### Settings for AeroDyn15

    case_inputs[("AeroDyn15","Wake_Mod")]  = {'vals':[0], 'group':0}     # Turning off BEM/DBEM
    case_inputs[("AeroDyn15","AFAeroMod")]  = {'vals':[0], 'group':0}   # Running AF aero seperatly #######################################################################
    
    # If unsteady airfoil aerodynamics is used, then the following settings are needed
    if case_inputs[("AeroDyn15","AFAeroMod")]['vals'][0] == 2:
        case_inputs[("AeroDyn15","UA_Mod")]      = {'vals':[4], 'group':4} #, 4], 'group':4}   # GE: 1-state B-L model
    else:
        case_inputs[("AeroDyn15","UA_Mod")]      = {'vals':[0], 'group':0}

    case_inputs[("AeroDyn15","TwrPotent")]  = {'vals':[0], 'group':0}   # Turning off tower potential flow
    case_inputs[("AeroDyn15","TwrShadow")]  = {'vals':[0], 'group':0}   # Turning off tower shadow


    ##### Settings for Structural

    # Setting both Idling and parked conditions, lets set it as the last config
    # Idling has no brake! can be applied
    lastGroup = 5
    # case_inputs[("ElastoDyn","GenDOF")]     = {'vals':['True','True'], 'group':lastGroup} # First -> Idle, 2nd -> Locked rotor
    # case_inputs[("Fst","CompServo")]        = {'vals':[1, 1], 'group':lastGroup} # Same as above
    # case_inputs[("ServoDyn","PCMode")]      = {'vals':[0, 0], 'group':lastGroup} # Same as above
    # case_inputs[("ServoDyn","VSContrl")]    = {'vals':[0, 0], 'group':lastGroup} # Same as above
    # case_inputs[("ServoDyn","GenTiStr")]    = {'vals':['True', 'True'], 'group':lastGroup} # Same as above
    # case_inputs[("ServoDyn","TimeGenOn")]   = {'vals':[2000, 2000], 'group':lastGroup} # Same as above

    ####### Idling ONLY case #######3
    case_inputs[("ElastoDyn","GenDOF")]     = {'vals':['True'], 'group':lastGroup} # First -> Idle, 2nd -> Locked rotor
    case_inputs[("Fst","CompServo")]        = {'vals':[1], 'group':lastGroup} # Same as above
    case_inputs[("ServoDyn","PCMode")]      = {'vals':[0], 'group':lastGroup} # Same as above
    case_inputs[("ServoDyn","VSContrl")]    = {'vals':[0], 'group':lastGroup} # Same as above
    case_inputs[("ServoDyn","GenTiStr")]    = {'vals':['True'], 'group':lastGroup} # Same as above
    case_inputs[("ServoDyn","TimGenOn")]   = {'vals':[3000], 'group':lastGroup} # Same as above
    



    # # Modling the DiveTrain ringing!
    # case_inputs[("ElastoDyn","DrTrDOF")]     = {'vals':['True'], 'group':0}

    case_inputs[("ElastoDyn","BlPitch1")]   = {'vals': [90], 'group': 0}  # Pitching to feather
    case_inputs[("ElastoDyn","BlPitch2")]   = case_inputs[("ElastoDyn","BlPitch1")]  # Setting pitch angle; B1 to be used for offset.
    case_inputs[("ElastoDyn","BlPitch3")]   = case_inputs[("ElastoDyn","BlPitch2")]
    case_inputs[("ElastoDyn","Azimuth")]    = {'vals': [0], 'group': 2} # Relying on rotor symmetry, must be [0, 360) degrees); so 300, 330, 0, 30, 60
    case_inputs[("ElastoDyn","RotSpeed")]   = {'vals': [0], 'group': 0} # Setting to be stand-still

    # case_inputs[("ElastoDyn","NacYaw")]     = {'vals': np.linspace(-179,180,33), 'group': 3} # Yaw angles  np.linspace(-50,50,21)

    case_inputs[("ElastoDyn","NacYaw")]     = {'vals': np.array([-179., -165., -150., -135., -120., -105.,  -90.,  -75.,  -60., -45.,  -30., # 15 deg spec as per IEC
                                                                -20., -15., -10.,  -5.,   0.,   5.,  10.,  15.,  20., # higher resolution between -20 and 20 deg
                                                                30.,   45.,   60.,   75., 90.,  105.,  120.,  135.,  150.,  165.,  180.]), 'group': 3} # Yaw angles  np.linspace(-50,50,21)

    # Test Case 09AUG24
    # case_inputs[("ElastoDyn","NacYaw")]     = {'vals': [0], 'group': 3} # Yaw angles  np.linspace(-50,50,21)
    # case_inputs[("ElastoDyn","NacYaw")]     = {'vals': np.linspace(-10,10,3), 'group': 3} # Yaw angles  np.linspace(-50,50,21)


    # case_inputs[("ElastoDyn","TwrFile")]    = {'vals': ['IEA-15-240-RWT-Onshore_ElastoDyn_tower_soft.dat'], 'group': 0} # Soft tower to account for monopile dynamics

    ##### Settings for Inflows!!

    turbFiles=['/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_1.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_2.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_3.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_4.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_5.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_6.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_7.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_8.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_9.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_10.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_11.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_12.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_13.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_14.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_15.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_16.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_17.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_18.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_19.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_20.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_21.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_22.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_23.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_24.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_25.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_26.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_27.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_28.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_29.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_30.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_31.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_32.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_33.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_34.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_35.bts', 
                '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/withRamp/ramp_plus_turb_36.bts', 
]
    

#     turbFiles=[ '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_1.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_2.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_3.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_4.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_5.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_6.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_7.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_8.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_9.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_10.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_11.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_12.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_13.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_14.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_15.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_16.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_17.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_18.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_19.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_20.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_21.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_22.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_23.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_24.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_25.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_26.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_27.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_28.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_29.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_30.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_31.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_32.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_33.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_34.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_35.bts', 
#                 '/projects/storm/IdlingRotor/models/inflow/higherResolution/withRamp/ramp_plus_turb_36.bts', 
# ]

    # turbFiles=[ '/projects/storm/IdlingRotor/models/inflow/hurricane_les_36seeds/preRamp/15mw-typhoon-TEWM50_Seed1.bts', ]

    case_inputs[("InflowWind","WindType")]  = {'vals':[3], 'group':0}
    case_inputs[("InflowWind","FileName_BTS")]= {'vals': turbFiles, 'group': 1} # forcing WS

    # case_inputs[("InflowWind","WindType")]  = {'vals':[1], 'group':0}
    # case_inputs[("InflowWind","HWindSpeed")]= {'vals': [79.8], 'group': 0} # forcing WS
    # case_inputs[("InflowWind","PLexp")]= {'vals': [0.11], 'group': 0} # forcing WS power law

    # Handling the OpenFAST version
    if kestrelFlag:
        dll = ["/usr/share/miniconda3/envs/test/lib/libdiscon.so"]
        fastBatch.FAST_exe = '/projects/bar/mchetan/tools/openfast/tightCoupling-mc/build/glue-codes/openfast/openfast'
        # fastBatch.FAST_exe = '/projects/storm/IdlingRotor/tools/openfast/of-v351/build/glue-codes/openfast/openfast'
    elif platform == 'darwin':
        dll = ["/Users/mchetan/Desktop/nrel/projects/bar/instability-raaw/numericalWork/rosco/rosco-mc-dev/ROSCO/build/libdiscon.dylib"]
        fastBatch.FAST_exe = '/Users/mchetan/Desktop/nrel/projects/bar/instability-raaw/numericalWork/openfast-v3-2'

    # case_inputs[("ServoDyn","DLL_FileName")] = {'vals': dll, 'group': 0}

    # Generate the matrix of cases
    case_list, case_name_list = CaseGen_General(case_inputs, dir_matrix=fastBatch.FAST_runDirectory, namebase='storm-test')

    fastBatch.case_list = case_list
    fastBatch.case_name_list = case_name_list
    fastBatch.use_exe = True
    fastBatch.allow_fails = True

    onlyFiles = False # Write only the files; EXPERIMENTAL

    with open(f'{fastBatch.FAST_runDirectory}/case_inputs.pkl', 'wb') as handle:
        pickle.dump((case_inputs, fastBatch) , handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Run OpenFAST, either serially or sequentially
    if onlyFiles:
        fastBatch.writeFilesOnly()
    elif n_cores == 1:
        summary_stats, extreme_table, DELs, Damage, ct = fastBatch.run_serial()
    else:
        summary_stats, extreme_table, DELs, Damage, ct = fastBatch.run_multi(n_cores)


