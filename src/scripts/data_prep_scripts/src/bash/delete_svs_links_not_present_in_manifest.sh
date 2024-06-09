#!/bin/bash

# Function to delete symbolic links that are not present in the provided text file
delete_links_not_in_list() {
    local link_dir="$1"
    local file_list="$2"

    # Read filenames from the list into an array
    declare -A valid_filenames
    while IFS= read -r filename; do
        valid_filenames["$filename"]=1
    done < "$file_list"

    # Find and delete symbolic links not in the list
    find "$link_dir" -type l | while read -r link; do
        target=$(readlink "$link")
        base_target=$(basename "$target")
        if [[ -z "${valid_filenames[$base_target]}" ]]; then
            rm -f "$link"
        fi
    done
}

# Check for correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 link_directory file_list.txt"
    exit 1
fi

# Assign arguments to variables
LINK_DIR="$1"
FILE_LIST="$2"

# Call the function to delete links not in the list
delete_links_not_in_list "$LINK_DIR" "$FILE_LIST"

echo "Symbolic links not in $FILE_LIST have been deleted from $LINK_DIR"
