import os
import pandas as pd

source_dir = '../../../../rna'  # Update this path
target_csv = '../compiled_gene_counts.csv'  # Update this path

compiled_data = {}

def process_file(file_path, sample_id):
    df = pd.read_csv(file_path, sep='\t', comment='#')
    if 'gene_name' in df.columns and 'tpm_unstranded' in df.columns:
        for _, row in df.iterrows():
            gene_name = row['gene_name']
            unstranded = row['tpm_unstranded']
            if gene_name not in compiled_data:
                compiled_data[gene_name] = {}
            compiled_data[gene_name][sample_id] = unstranded

for subdir, _, files in os.walk(source_dir):
    for file in files:
        if file.endswith('.rna_seq.augmented_star_gene_counts.tsv'):
            sample_id = os.path.basename(subdir)
            file_path = os.path.join(subdir, file)
            process_file(file_path, sample_id)

compiled_df = pd.DataFrame.from_dict(compiled_data, orient='index').fillna(0)

compiled_df.reset_index(inplace=True)
compiled_df.rename(columns={'index': 'gene_name'}, inplace=True)

compiled_df.to_csv(target_csv, index=False)

print(f"Compiled data saved to {target_csv}")
