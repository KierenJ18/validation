#!/bin/bash
# filepath: /vols/hyperk/users/kj4718/validation/processing/batch_analysis.sh

# Check if correct number of arguments provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <base_directory>"
    echo "Example: $0 /vols/hyperk/WCSimvalidation/HKFD/"
    exit 1
fi

BASE_DIR="$1"
ANALYSIS_SCRIPT="/vols/hyperk/users/kj4718/validation/processing/analysis_script.sh"
DAQ_READFILE="/vols/hyperk/users/kj4718/validation/processing/daq_readfilemain_v1.12.22"
OUTPUT_BASE="/vols/hyperk/users/kj4718/validation/analysed_results"

# Check if base directory exists
if [ ! -d "$BASE_DIR" ]; then
    echo "Error: Base directory $BASE_DIR does not exist"
    exit 1
fi

# Check if analysis script exists
if [ ! -f "$ANALYSIS_SCRIPT" ]; then
    echo "Error: Analysis script $ANALYSIS_SCRIPT does not exist"
    exit 1
fi

# Get the parent folder name from BASE_DIR (e.g., HKFD from /vols/hyperk/WCSimvalidation/HKFD/)
PARENT_FOLDER=$(basename "$BASE_DIR")

echo "Processing folders in: $BASE_DIR"
echo "Results will be saved to: $OUTPUT_BASE/$PARENT_FOLDER/"

# Loop through all directories in BASE_DIR
for folder in "$BASE_DIR"*/; do
    # Check if it's actually a directory
    if [ ! -d "$folder" ]; then
        continue
    fi
    
    # Get folder name
    folder_name=$(basename "$folder")
    echo "Processing folder: $folder_name"
    
    # Check if rwcs subdirectory exists
    rwcs_dir="${folder}rwcs/"
    if [ ! -d "$rwcs_dir" ]; then
        echo "Warning: rwcs directory not found in $folder_name, skipping..."
        continue
    fi
    
    # Create output directory structure if it doesn't exist
    output_dir="$OUTPUT_BASE/$PARENT_FOLDER/$folder_name/wcsimrootevent_OD"
    if [ ! -d "$output_dir" ]; then
        echo "Creating output directory: $output_dir"
        mkdir -p "$output_dir"
    fi
    
    # Run the analysis script
    echo "Running analysis for $folder_name..."
    source "$ANALYSIS_SCRIPT" "$rwcs_dir" "$DAQ_READFILE" "wcsimrootevent_OD" "$output_dir"
    
    # Check if the command was successful
    if [ $? -eq 0 ]; then
        echo "Successfully processed $folder_name"
    else
        echo "Error processing $folder_name"
    fi
    
    echo "----------------------------------------"
done

echo "Batch processing complete!"