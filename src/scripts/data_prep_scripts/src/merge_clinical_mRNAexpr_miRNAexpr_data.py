import csv
import os

# def append_expression_data_to_tsv(clinical_tsv, expression_csv, trait, output_tsv_file):
#     # Read the CSV file and find the relevant row
#     with open(expression_csv, 'r', newline='', encoding='utf-8') as csvfile:
#         csv_reader = csv.DictReader(csvfile)
#         csv_column_names = csv_reader.fieldnames
#         csv_row_data = {}
#         for row in csv_reader:
#             row_header =row[csv_column_names[0]]
#             if trait.lower().strip() in row_header.lower().strip():
#                 csv_row_data = row
#                 break
#
#     if not csv_row_data:
#         print(f"No matching row found in CSV for {trait}")
#         return
#
#     # Read the TSV file and append the relevant row data from the CSV
#     with open(clinical_tsv, 'r', newline='', encoding='utf-8') as tsvfile:
#         tsv_reader = csv.DictReader(tsvfile, delimiter='\t')
#         tsv_fieldnames = tsv_reader.fieldnames
#         tsv_rows = list(tsv_reader)
#
#     # Add new column to TSV fieldnames
#     new_fieldnames = tsv_fieldnames + [trait]
#
#     # Append CSV row data to each TSV row based on the "Sample ID" match
#     for tsv_row in tsv_rows:
#         sample_id = tsv_row['Sample ID']
#         tsv_row[trait] = csv_row_data.get(sample_id, '')
#
#     # Write the new TSV file with the appended column
#     with open(output_tsv_file, 'w', newline='', encoding='utf-8') as outfile:
#         tsv_writer = csv.DictWriter(outfile, fieldnames=new_fieldnames, delimiter='\t')
#         tsv_writer.writeheader()
#         tsv_writer.writerows(tsv_rows)
#
#     print(f"New TSV file saved as {output_tsv_file}")

import pandas as pd


def append_expression_data_to_tsv(tsv_file, csv_file, match_string, output_file):
    # Read the TSV and CSV files
    tsv_df = pd.read_csv(tsv_file, sep='\t')
    csv_df = pd.read_csv(csv_file)

    # Find the row in the CSV file that matches the provided string in the first column
    matching_row = csv_df[csv_df.iloc[:, 0] == match_string.lower()]

    if matching_row.empty:
        matching_row = csv_df[csv_df.iloc[:, 0] == match_string]
    if matching_row.empty:
        print(f"No matching row found for string '{match_string}' in the CSV file.")
        return

    # Extract the matching row as a dictionary
    matching_row_dict = matching_row.iloc[0].to_dict()

    # Initialize the new column values list
    new_column_values = []

    # Add a new column to the TSV based on the matching row values
    for idx, row in tsv_df.iterrows():
        sample_id = row.get('Sample ID')
        patient_id = row.get('Patient ID')
        if sample_id in matching_row_dict:
            new_column_values.append(matching_row_dict[sample_id])
        elif patient_id in matching_row_dict:
            new_column_values.append(matching_row_dict[patient_id])
        else:
            new_column_values.append(None)

    # Add the new column to the TSV dataframe
    new_column_name = f'New Column from {match_string}'
    tsv_df[new_column_name] = new_column_values

    # Save the modified TSV as a new CSV file
    tsv_df.to_csv(output_file, index=False)
    print(f"Modified TSV saved as '{output_file}'")


d1 ={
    "base_file": '/home/mathias/DSitLS/dsitls-project/scripts/data_prep_scripts/TCGA-COAD/'
                 'coadread_tcga_clinical_data_incl_survival.tsv',
    "csv_path": "/home/mathias/DSitLS/dsitls-project/scripts/data_prep_scripts/TCGA-COAD/"
                "compiled_mirnas_quantification.csv",
    "trait": "hsa-miR-143",
    "out_path": "/home/mathias/DSitLS/dsitls-project/scripts/data_prep_scripts/TCGA-COAD/"
                "coadread_tcga_clinical_data_incl_miRNA.csv"}
d2 ={
    "base_file": d1["out_path"],
    "csv_path": "/home/mathias/DSitLS/dsitls-project/scripts/data_prep_scripts/TCGA-COAD/compiled_gene_counts.csv",
    "trait": "PIGR",
    "out_path": "/home/mathias/DSitLS/dsitls-project/scripts/data_prep_scripts/TCGA-COAD/"
                "coadread_tcga_clinical_data_complete.csv"}

input_dicts = [d1, d2]

for input_dict in input_dicts:
    tsv_file = input_dict['base_file']
    csv_file = input_dict['csv_path']
    search_string = input_dict['trait']
    output_file = input_dict['out_path']
    append_expression_data_to_tsv(tsv_file, csv_file, search_string, output_file)
