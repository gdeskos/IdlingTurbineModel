#!/bin/sh

# Bash script to go into the different OpenFAST run directories and check the status of the simulations, then tabulate the results

# Variables
mainPath="./"
simTypes=("CAT1" "CAT2" "CAT3" "CAT4" "CAT5")
afTypes=("steady" "unsteady")



# File to write the results to per simulation type and afType
resultsFile="SimulationResults.txt"
# Create the file, delete if it already exists
if [ -f $resultsFile ]
then
    rm $resultsFile
fi
touch $resultsFile


# Loop through the different simulation types

for simType in ${simTypes[@]}
do
    for afType in ${afTypes[@]}
    do
        # Go into the directory
        path2Dir="${mainPath}/${simType}/${afType}"
        echo "Checking status of simulations in ${path2Dir}"

        # get all the files to check the status of
        files=$(find -wholename "${path2Dir}/*.stdOut")

        # setting loop vars
        numSuccess=0
        numFail=0

        # looping over output status files
        for file in ${files[@]}
        do
            # Get the name of the file
            fileName=$(basename $file)
            echo "Checking status of ${fileName} in ${path2Dir}"

            # need to check if the third line from the bottom contains "OpenFAST terminated normally." account for whitespaces before and after the string
            # if it does, then the simulation was successful, otherwise it failed
            status=$(tail -n 3 $file | grep -q "OpenFAST terminated normally.")
            if [ $? -eq 0 ]
            then
                echo "Simulation ${fileName} was successful"
                numSuccess=$((numSuccess+1))
            else
                echo "Simulation ${fileName} failed"
                numFail=$((numFail+1))
            fi


        done

        # Write the results to the results file
        echo "Simulation type: ${simType}" >> $resultsFile
        echo "AF type: ${afType}" >> $resultsFile
        echo "Number of successful simulations: ${numSuccess}" >> $resultsFile
        echo "Number of failed simulations: ${numFail}" >> $resultsFile
        echo "-----------------------------" >> $resultsFile
    done
done

echo "All simulations have been checked and results have been written to ${resultsFile}"
