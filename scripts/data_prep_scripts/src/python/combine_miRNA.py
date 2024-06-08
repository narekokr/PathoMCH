import os
import pandas as pd

source_dir = '../../../../rna'  # Update this path
target_csv = '../compiled_mirnas_quantification.csv'  # Update this path

compiled_data = {}

def process_file(file_path, sample_id):
    df = pd.read_csv(file_path, sep='\t')
    if 'miRNA_ID' in df.columns and 'reads_per_million_miRNA_mapped' in df.columns:
        for _, row in df.iterrows():
            mirna_id = row['miRNA_ID']
            read_count = row['reads_per_million_miRNA_mapped']
            if mirna_id not in compiled_data:
                compiled_data[mirna_id] = {}
            compiled_data[mirna_id][sample_id] = read_count

for subdir, _, files in os.walk(source_dir):
    for file in files:
        if file.endswith('.mirnas.quantification.txt'):
            sample_id = os.path.basename(subdir)
            file_path = os.path.join(subdir, file)
            process_file(file_path, sample_id)

compiled_df = pd.DataFrame.from_dict(compiled_data, orient='index').fillna(0)

compiled_df.reset_index(inplace=True)
compiled_df.rename(columns={'index': 'miRNA_ID'}, inplace=True)

compiled_df.to_csv(target_csv, index=False)

print(f"Compiled data saved to {target_csv}")
