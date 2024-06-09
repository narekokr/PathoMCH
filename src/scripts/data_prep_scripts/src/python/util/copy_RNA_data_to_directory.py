import os
import shutil
from pathlib import Path

def copy_txt_files(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    copied = 0

    for root, dirs, files in os.walk(input_dir):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            new_output_subdir = Path(os.path.join(output_dir, dir_name))
            if not Path(new_output_subdir).name.startswith("TCGA"):
                new_output_subdir = os.path.join(output_dir,Path(os.path.join(root, dir_name)).parent)
            copied_any_file = False

            for subroot, subdirs, subfiles in os.walk(dir_path):
                # Skip logs subsubdirectory
                if 'logs' in subdirs:
                    subdirs.remove('logs')

                for file_name in subfiles:
                    if (file_name.endswith('.txt') and file_name != 'annotations.txt') or file_name.endswith('.tsv'):
                        # Ensure the new output subdirectory exists
                        if not os.path.exists(new_output_subdir):
                            os.makedirs(new_output_subdir)

                        # Copy the file to the new directory
                        src_file_path = os.path.join(subroot, file_name)
                        if not Path(new_output_subdir).name.startswith("TCGA"):
                            print("jo")
                            pass
                        dest_file_path = os.path.join(new_output_subdir, file_name)
                        if not os.path.exists(dest_file_path):
                            shutil.copy2(src_file_path, dest_file_path)
                            copied += 1
                            copied_any_file = True

            # Remove new_output_subdir if no files were copied
            # if not copied_any_file and os.path.exists(new_output_subdir):
            #     os.rmdir(new_output_subdir)
    print(f'Copied {copied} txt files')

# input_dir = '/home/mathias/DSitLS/project/TCGA-COAD/DATA_CONTAINIG_SVS_FILES/files/'
input_dir = '/home/mathias/DSitLS/project/TCGA-COAD/DATA_CONTAINIG_SVS_FILES/sorted_files/'
output_dir = '/home/mathias/DSitLS/project/TCGA-COAD/RNA_DATA/'

copy_txt_files(input_dir, output_dir)
