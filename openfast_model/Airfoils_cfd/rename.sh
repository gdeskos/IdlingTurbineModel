#!/bin/bash

# Loop through all matching files
for file in DLC1.1_0_weis_job_0_AeroDyn_Polar_*.dat; do
    # Extract the number part (XX) from the filename
    number=$(echo "$file" | grep -o "[0-9]\+" || echo "0")
    
    # Format the number with leading zero if needed
    if [[ -n "$number" ]]; then
        formatted_number=$(printf "%02d" "$number")
    else
        echo "Error: Could not extract number from filename $file"
        continue
    fi
    
    # Create new filename
    new_name="IEA-15-240-RWT_AeroDyn15_Polar_${formatted_number}.dat"
    
    # Rename the file
    mv "$file" "$new_name"
    echo "Renamed: $file -> $new_name"
done