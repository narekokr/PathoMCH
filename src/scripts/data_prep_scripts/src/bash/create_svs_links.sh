#!/bin/bash

# Function to create symbolic links for .svs files
create_links() {
    local directory="$1"
    local file_list="$2"
    local output_dir="$3"

    # Check if the output directory exists, if not, create it
    [ ! -d "$output_dir" ] && mkdir -p "$output_dir"

    # If a file list is provided, read filenames from the list
    if [ -n "$file_list" ]; then
        while IFS= read -r filename; do
            find "$directory" -type f -name "$filename" -exec ln -s {} "$output_dir" \;
        done < "$file_list"
    else
        # Find all .svs files and create symbolic links
        find "$directory" -type f -name "*.svs" -exec ln -s {} "$output_dir" \;
    fi
}

# Check for correct number of arguments
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <directory> <output_directory> [file_list.txt]"
    exit 1
fi

# Assign arguments to variables
DIRECTORY="$1"
OUTPUT_DIR="$2"
FILE_LIST="${3:-}"

# Call the function to create links
create_links "$DIRECTORY" "$FILE_LIST" "$OUTPUT_DIR"

echo "Symbolic links created in $OUTPUT_DIR"
