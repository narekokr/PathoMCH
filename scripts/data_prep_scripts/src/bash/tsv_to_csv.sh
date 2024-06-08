#!/bin/bash

# Check for correct number of arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 input.tsv output.csv"
    exit 1
fi

# Assign arguments to variables
input_file="$1"
output_file="$2"

# Translate .tsv to .csv by replacing all tabs with commas
sed 's/\t/,/g' "$input_file" > "$output_file"

echo "Conversion complete: $input_file to $output_file"
