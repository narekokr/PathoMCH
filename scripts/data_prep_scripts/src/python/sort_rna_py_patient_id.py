import os
import pandas as pd
import shutil

file_path = '../../../../gdc_sample_sheet.2024-06-08.tsv'
data = pd.read_csv(file_path, sep='\t')
print(data.columns)
source_dir = '../../../../gdc-data'  # Update this path
target_dir = '../../../../rna'  # Update this path

os.makedirs(target_dir, exist_ok=True)

for _, row in data.iterrows():
    file_id = row['File ID']
    sample_id = row['Sample ID']
    file_name = row['File Name']

    if file_name.endswith('.svs'):
        continue

    source_file_path = os.path.join(source_dir, file_id, file_name)

    target_subfolder_path = os.path.join(target_dir, sample_id)

    os.makedirs(target_subfolder_path, exist_ok=True)

    target_file_path = os.path.join(target_subfolder_path, file_name)

    shutil.copy2(source_file_path, target_file_path)

print("Files have been successfully reorganized.")
