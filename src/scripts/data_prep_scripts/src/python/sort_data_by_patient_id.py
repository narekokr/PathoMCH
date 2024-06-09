import os
import shutil
import csv
from pathlib import Path
from distutils.dir_util import copy_tree

def generate_id_dict(tsv_path, main_id_col, other_id_cols):
    id_dict = {}
    with open(tsv_path, 'r', newline='') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            main_id = row[main_id_col]
            other_ids = {col: row[col] for col in other_id_cols}
            id_dict[main_id] = other_ids
    return id_dict

def process_directories(id_dict, input_dir, output_dir, dummy=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    directories_to_be_moved =[]

    for root, dirs, files in os.walk(input_dir, topdown=False):
        for name in dirs:
            if name=="logs":
                # we probably find no ids here
                break
            dir_path = os.path.join(root, name)
            matched_main_id = None

            for main_id, ids in id_dict.items():
                all_ids = [main_id.lower()] + [entry.lower() for entry in list(ids.values())]
                if name.lower() in all_ids:
                    # directory name contains any id
                    matched_main_id = main_id
                    directories_to_be_moved.append({
                        matched_main_id: dir_path
                    })
                    break

                if not matched_main_id:
                    #no match in dirname, we look at files
                    for filename in os.listdir(dir_path):
                        file_path = os.path.join(dir_path, filename)
                        if "annotations" in filename:
                            # we have annotation.txt
                            with open(file_path, 'r') as file:
                                content = file.read()
                                if any(id.lower() in content.lower() for id in all_ids):
                                    # somewhere in the file any ID matches
                                    matched_main_id = main_id
                                    directories_to_be_moved.append({
                                        matched_main_id : dir_path
                                    })
                                    break
                        elif any(id.lower() in filename.lower() for id in all_ids):
                            # we look for ID in filenames, that are not annotation
                            matched_main_id = main_id
                            directories_to_be_moved.append({
                                matched_main_id: dir_path
                            })
                            break
            # matched_main_id = None



    if directories_to_be_moved:
        move_count = 0
        for dir_dicts in directories_to_be_moved:
            for ID, path in dir_dicts.items():
                new_dir_path = os.path.join(output_dir, ID)
                if dummy:
                    copy_tree(path, new_dir_path)
                else:
                    if not os.path.exists(new_dir_path):
                        os.makedirs(new_dir_path)
                    shutil.move(path, new_dir_path)
                move_count += 1

        print(f"{move_count} files moved successfully")


if __name__ == "__main__":

#   tsv_path = Path('/home/mahias/Downloads/coadread_tcga_clinical_data.tsv')
#    id_dict = generate_id_dict(tsv_path, main_id_col, other_id_cols)
#
#    input_dir = Path('/home/mahias/Downloads/gdc-client_v1.6.1_Ubuntu_x64/the_shit_so_far')
#    output_dir = Path('/home/mahias/Downloads/gdc-client_v1.6.1_Ubuntu_x64/sorted')

####coared_style
    # tsv_path = Path('/home/mahias/DSitLS/project/TCGA-COAD/coadread_tcga_clinical_data_incl_survival.tsv')
    # main_id_col = 'Patient ID'
    # other_id_cols = ['Patient ID', 'Sample ID', 'Other Patient ID', 'Other Sample ID', 'Pathology report uuid']
    #
    # id_dict = generate_id_dict(tsv_path, main_id_col, other_id_cols)
    #
    # input_dir = Path('/home/mahias/DSitLS/project/TCGA-COAD/files')
    # output_dir = Path('/home/mahias/DSitLS/project/TCGA-COAD/sorted_files')
    # process_directories(id_dict, input_dir, output_dir)

#####other
    # tsv_path = Path('/home/mathias/DSitLS/project/TCGA-COAD/gdc_sample_sheet.2024-06-01.tsv')
    # main_id_col = 'Case ID'
    # other_id_cols = ['Case ID', 'Sample ID', 'File ID', 'File Name']
    #
    # id_dict = generate_id_dict(tsv_path, main_id_col, other_id_cols)
    #
    # input_dir = Path('/home/mathias/DSitLS/project/TCGA-COAD/DATA_CONTAINIG_SVS_FILES/files')
    # output_dir = Path('/home/mathias/DSitLS/project/TCGA-COAD/DATA_CONTAINIG_SVS_FILES/sorted_files')
    # process_directories(id_dict, input_dir, output_dir)

#### dummy data
    tsv_path = Path('/home/mathias/DSitLS/project/TCGA-COAD/coadread_tcga_clinical_data_incl_survival.tsv')
    main_id_col = 'Patient ID'
    other_id_cols = ['Patient ID', 'Sample ID', 'Other Patient ID', 'Other Sample ID', 'Pathology report uuid']

    id_dict = generate_id_dict(tsv_path, main_id_col, other_id_cols)

    input_dir = Path('/home/mathias/DSitLS/project/TCGA-COAD/dummy_data/files')
    output_dir = Path('/home/mathias/DSitLS/project/TCGA-COAD/dummy_data/sorted_dummy')
    process_directories(id_dict, input_dir, output_dir, dummy=True)
    pass