import os
import pandas as pd

# Read the manifest file into a DataFrame
# file_path = '/home/mathias/DSitLS/old_project/TCGA-COAD/manifest_part2.txt'
# file_path = '/home/mathias/DSitLS/old_project/TCGA-COAD/quality_check/maybe.txt'
# file_path = '/home/mathias/DSitLS/old_project/TCGA-COAD/quality_check/yes.txt'
# file_path = '/home/mathias/DSitLS/old_project/TCGA-COAD/quality_check/yes_narek.txt'
file_path = '/home/mathias/DSitLS/old_project/TCGA-COAD/quality_check/maybe_narek.txt'
df = pd.read_csv(file_path, sep='\t')

# Get the list of subfolder IDs
subfolder_ids = df['id'].tolist()

# Define the source directory containing all subfolders and the target directory for accessible subfolders
source_directory = '/home/mathias/DSitLS/old_project/TCGA-COAD/DATA_CONTAINIG_SVS_FILES/files'
# target_directory = '/home/mathias/DSitLS/old_project/TCGA-COAD/svs_links'
target_directory = '/home/mathias/DSitLS/old_project/TCGA-COAD/svs_links_maybe_narek'

# Create the target directory if it does not exist
os.makedirs(target_directory, exist_ok=True)

# Create symbolic links for each subfolder ID
for subfolder_id in subfolder_ids:
    source_dir_path = os.path.join(source_directory, subfolder_id)
    target_path = os.path.join(target_directory, subfolder_id)
    # target_path = target_directory
    print(target_path)
    # Check if the source path exists before creating the symlink
    if os.path.exists(source_dir_path):
        [os.symlink(os.path.join(source_dir_path, file), target_path) for file in os.listdir(source_dir_path) if 
         file.endswith('.svs')]
    else:
        print(f"Source path does not exist: {source_path}")

print("Symbolic links created successfully.")
