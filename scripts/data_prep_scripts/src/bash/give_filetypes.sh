#!/bin/bash
# generated with chatGPT
# Initialize an empty associative array to store unique file extensions
declare -A file_extensions

# Find all files in the current directory and its subdirectories
# Use a loop to extract file extensions and store them in the associative array
while IFS= read -r -d '' file; do
    extension="${file##*.}"
    if [[ "$extension" != "$file" ]]; then
        file_extensions["$extension"]=1
    fi
done < <(find . -type f -print0)

# Print all unique file extensions
for ext in "${!file_extensions[@]}"; do
    echo "$ext"
done

