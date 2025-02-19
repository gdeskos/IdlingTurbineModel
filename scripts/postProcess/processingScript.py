
import numpy as np
import pandas as pd
import os, sys, glob
# import pickle
from multiprocessing import Pool
import argparse

from weis.aeroelasticse import FileTools

sys.path.append(os.path.abspath("/projects/storm/IdlingRotor/tools/pyDatView/pydatview/tools"))

from fatigue import *

# Add arguments to the script
parser = argparse.ArgumentParser(description='Process OpenFAST output files to get stats')
parser.add_argument('--path', type=str, help='Path to the OpenFAST output files')

args = parser.parse_args()

additionalSavePath = '/projects/storm/IdlingRotor/i_devFiles/processedFiles'


def process_Stats(openfastDF, fileName= None, startTime = 520.0, expandedDf = None):
    # Passed the OpenFAST dataframe, returns a dataframe with the stats for all the channels

    statsDF = pd.DataFrame(index = openfastDF.columns,  columns=['mean', 'std', 'median', 'max', 'min', 'DEL5', 'DEL10', 'DEL12'])

    if expandedDf is not None:
        statsDF2 = pd.DataFrame(index = expandedDf.columns,  columns=['mean', 'std', 'median', 'max', 'min', 'DEL5', 'DEL10', 'DEL12'])
        statsDF = pd.concat([statsDF, statsDF2])

    success = True

    # Trim the data to start at startTime, if empty, write to error file and use whole data
    temp = openfastDF[openfastDF[('Time', '(s)')] >= startTime]

    if temp.empty:
        print(f'No data after {startTime} seconds')
        
        with open('error_FinalRun.txt', 'a') as f:
            f.write(f"{fileName} has no data after {openfastDF[('Time', '(s)')][len(openfastDF[('Time', '(s)')])-1]} seconds\n")

        temp = openfastDF

        success = False

    for col in temp.columns:

        # print(f'working on {col}')

        if col == ('Time', '(s)'):
            continue

        statsDF.loc[col] = [
                            temp[col].mean(), 
                            temp[col].std(), 
                            temp[col].median(),
                            temp[col].max(), 
                            temp[col].min(),
                            equivalent_load(temp[('Time', '(s)')], temp[col], m=5), 
                            equivalent_load(temp[('Time', '(s)')], temp[col], m=10), 
                            equivalent_load(temp[('Time', '(s)')], temp[col], m=12),
                            ]

    if expandedDf is not None:

        # Calculate the combined loading channels
        B1RootMxyr = np.sqrt(temp[('B1RootMxr','(N-m)')]**2 + temp[('B1RootMyr','(N-m)')]**2)
        B2RootMxyr = np.sqrt(temp[('B2RootMxr','(N-m)')]**2 + temp[('B2RootMyr','(N-m)')]**2)
        B3RootMxyr = np.sqrt(temp[('B3RootMxr','(N-m)')]**2 + temp[('B3RootMyr','(N-m)')]**2)

        YawBrMxyp = np.sqrt(temp[('YawBrMxp','(kN-m)')]**2 + temp[('YawBrMyp','(kN-m)')]**2)
        TwrBsMxyt = np.sqrt(temp[('TwrBsMxt','(kN-m)')]**2 + temp[('TwrBsMyt','(kN-m)')]**2)



        statsDF.loc[(    'B1RootMxyr',  '(N-m)')] = [
                                                        B1RootMxyr.mean(), 
                                                        B1RootMxyr.std(), 
                                                        B1RootMxyr.median(),
                                                        B1RootMxyr.max(), 
                                                        B1RootMxyr.min(),
                                                        equivalent_load(temp[('Time', '(s)')], B1RootMxyr, m=5), 
                                                        equivalent_load(temp[('Time', '(s)')], B1RootMxyr, m=10), 
                                                        equivalent_load(temp[('Time', '(s)')], B1RootMxyr, m=12)
                                                        ]
        statsDF.loc[(    'B2RootMxyr',  '(N-m)')] = [   
                                                        B2RootMxyr.mean(), 
                                                        B2RootMxyr.std(), 
                                                        B2RootMxyr.median(),
                                                        B2RootMxyr.max(), 
                                                        B2RootMxyr.min(),
                                                        equivalent_load(temp[('Time', '(s)')], B2RootMxyr, m=5), 
                                                        equivalent_load(temp[('Time', '(s)')], B2RootMxyr, m=10), 
                                                        equivalent_load(temp[('Time', '(s)')], B2RootMxyr, m=12),
                                    ]
        statsDF.loc[(    'B3RootMxyr',  '(N-m)')] = [
                                                        B3RootMxyr.mean(), 
                                                        B3RootMxyr.std(), 
                                                        B3RootMxyr.median(),
                                                        B3RootMxyr.max(), 
                                                        B3RootMxyr.min(),
                                                        equivalent_load(temp[('Time', '(s)')], B3RootMxyr, m=5), 
                                                        equivalent_load(temp[('Time', '(s)')], B3RootMxyr, m=10), 
                                                        equivalent_load(temp[('Time', '(s)')], B3RootMxyr, m=12),
                                    ]
        statsDF.loc[(     'YawBrMxyp', '(kN-m)')] = [
                                                        YawBrMxyp.mean(), 
                                                        YawBrMxyp.std(), 
                                                        YawBrMxyp.median(),
                                                        YawBrMxyp.max(), 
                                                        YawBrMxyp.min(),
                                                        equivalent_load(temp[('Time', '(s)')], YawBrMxyp, m=5), 
                                                        equivalent_load(temp[('Time', '(s)')], YawBrMxyp, m=10), 
                                                        equivalent_load(temp[('Time', '(s)')], YawBrMxyp, m=12),
                                    ]
        statsDF.loc[(     'TwrBsMxyt', '(kN-m)')] = [
                                                        TwrBsMxyt.mean(), 
                                                        TwrBsMxyt.std(), 
                                                        TwrBsMxyt.median(),
                                                        TwrBsMxyt.max(), 
                                                        TwrBsMxyt.min(),
                                                        equivalent_load(temp[('Time', '(s)')], TwrBsMxyt, m=5),
                                                        equivalent_load(temp[('Time', '(s)')], TwrBsMxyt, m=10), 
                                                        equivalent_load(temp[('Time', '(s)')], TwrBsMxyt, m=12),
                                    ]


    return statsDF, success

def wrapperFunc(file,verbose=True):
    if verbose:
        print(f'Processing {file}')
    df = pd.read_csv(file,skiprows=6,header=[0,1], dtype=np.float32,sep='\s+')
    dfExpanded = pd.read_csv('expandOF.txt',skiprows=6,header=[0,1], dtype=np.float32,sep='\s+')
    
    stats, success = process_Stats(df, fileName=file, expandedDf=dfExpanded)

    # assuming 2 levels of folders
    altPath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(file))))

    if success:
        stats.to_csv(file.replace('.out', '_stats.csv'), sep='\t')
        # stats.to_csv(file.replace(altPath,additionalSavePath).replace('.out', '_stats.csv'), sep='\t')
    else:
        stats.to_csv(file.replace('.out', '_stats_failed.csv'), sep='\t')
        # stats.to_csv(file.replace(altPath,additionalSavePath).replace('.out', '_stats_failed.csv'), sep='\t')

    if verbose:
        print(f' >>>>>> Done {file}')



pool = Pool(80)
path2run = args.path
files = [f'{path2run}/stormDlcs_{i:04d}.out' for i in range(0,1116)] # Running steady 500 - 1000

pool.map(wrapperFunc, files)
pool.close()
pool.join()

print('>>>>>>>>>>>>>>>> All done <<<<<<<<<<<<<<<<<<<<')