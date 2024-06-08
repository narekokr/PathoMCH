#!/bin/bash

# Function to move second-level directories to the output directory
move_second_level_directories() {
    local input_dir="$1"
    local output_dir="$2"

    # Check if the output directory exists, if not, create it
    [ ! -d "$output_dir" ] && mkdir -p "$output_dir"

    # Find and move all second-level directories
    find "$input_dir" -mindepth 2 -maxdepth 2 -type d -exec mv {} "$output_dir" \;
}


# Function to delete empty second-level directories
delete_empty_second_level_directories() {
    local input_dir="$1"

    # Find all second-level directories
    find "$input_dir" -mindepth 2 -maxdepth 2 -type d | while read -r dir; do
        # Check if the directory is empty
        if [ -z "$(ls -A "$dir")" ]; then
            rmdir "$dir"
            echo "Deleted empty directory: $dir"
        fi
    done
}

# Check for correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 input_directory output_directory"
    exit 1
fi

# Assign arguments to variables
INPUT_DIR="$1"
OUTPUT_DIR="$2"

# Call the function to move second-level directories
move_second_level_directories "$INPUT_DIR" "$OUTPUT_DIR"

echo "Second-level directories from $INPUT_DIR have been moved to $OUTPUT_DIR"

delete_empty_second_level_directories "$INPUT_DIR"
