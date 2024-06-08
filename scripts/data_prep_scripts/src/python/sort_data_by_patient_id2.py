import os
import shutil
import csv
from pathlib import Path
from distutils.dir_util import copy_tree
from shutil import copytree

def generate_id_dict(tsv_path, main_id_col, other_id_cols):
    id_dict = {}
    with open(tsv_path, 'r', newline='') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')
        for row in reader:
            main_id = row[main_id_col]
            other_ids = {col: row[col] for col in other_id_cols}
            id_dict[main_id] = other_ids
    return id_dict

def check_if_string_matches_any_id(myString, id_dict):
    for main_id, ids in id_dict.items():
        all_ids = [main_id.lower()] + [entry.lower() for entry in list(ids.values())]
        if myString.lower() in all_ids:
            return main_id
        elif any([myID.lower() in myString.lower() for myID in ids.values()]):
            return main_id
        else:
            return False

def process_directories(id_dict, input_dir, output_dir, dummy=False):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    directories_to_be_moved =[]

    for root, dirs, files in os.walk(input_dir, topdown=True):
        for dir_name in dirs:
            if dir_name=="logs":
                # we probably find no ids here
                break
            dir_path = os.path.join(root, dir_name)
            matched_main_id = check_if_string_matches_any_id(dir_name, id_dict)
            if matched_main_id:
                directories_to_be_moved.append({
                    matched_main_id: dir_path
                })
        for file_name in files:
            file_path = os.path.join(root, file_name)

            if file_name in ["timer.txt", "gdc-client"] or file_name.endswith("parcel"):
                break
            else:
                matched_main_id = check_if_string_matches_any_id(file_name, id_dict)
                if not matched_main_id:
                    contents=[]
                    with open(file_path, 'r') as file:
                        if file_name.endswith(".txt"):
                            contents = file.readlines()
                        elif file_name.endswith(".tsv"):
                            contents = csv.reader(file, delimiter='\t')
                        for line in contents:
                            matched_main_id = check_if_string_matches_any_id(line, id_dict)
                            if matched_main_id: break

            if matched_main_id:
                directories_to_be_moved.append({
                    matched_main_id: root
                })



            # for main_id, ids in id_dict.items():
            #     all_ids = [main_id.lower()] + [entry.lower() for entry in list(ids.values())]
            #     if dir_name.lower() in all_ids:
            #         # directory name contains any id
            #         matched_main_id = main_id
            #         directories_to_be_moved.append({
            #             matched_main_id: dir_path
            #         })
            #         break
            #
            #     if not matched_main_id:
            #         #no match in dirname, we look at files
            #         for filename in os.listdir(dir_path):
            #             file_path = os.path.join(dir_path, filename)
            #             if "annotations" in filename:
            #                 # we have annotation.txt
            #                 with open(file_path, 'r') as file:
            #                     content = file.read()
            #                     if any(id.lower() in content.lower() for id in all_ids):
            #                         # somewhere in the file any ID matches
            #                         matched_main_id = main_id
            #                         directories_to_be_moved.append({
            #                             matched_main_id : dir_path
            #                         })
            #                         break
            #             elif any(id.lower() in filename.lower() for id in all_ids):
            #                 # we look for ID in filenames, that are not annotation
            #                 matched_main_id = main_id
            #                 directories_to_be_moved.append({
            #                     matched_main_id: dir_path
            #                 })
            #                 break
            # # matched_main_id = None



    if directories_to_be_moved:
        move_count = 0
        for dir_dicts in directories_to_be_moved:
            for ID, path in dir_dicts.items():
                new_dir_path = os.path.join(output_dir, ID)
                if dummy:
                    if os.path.exists(new_dir_path):
                        shutil.rmtree(new_dir_path)
                    # copy_tree(path, new_dir_path)
                    copytree(path, new_dir_path, dirs_exist_ok=True)
                else:
                    if not os.path.exists(new_dir_path):
                        os.makedirs(new_dir_path)
                    shutil.move(path, new_dir_path)
                move_count += 1

        print(f"{move_count} files moved successfully")
        count_subdirs_and_files(output_dir)


def count_subdirs_and_files(base_dir):
    # used to check on sorting quality
    observations = set()

    for root, dirs, files in os.walk(base_dir):
        # We only want to process the first level subdirectories
        if root == base_dir:
            for subdir in dirs:
                subdir_path = os.path.join(root, subdir)
                subdirs_count = 0
                files_count = 0

                # Count subdirectories and files in the first-level subdirectory
                for _, subdirs, subfiles in os.walk(subdir_path):
                    subdirs_count += len(subdirs)
                    files_count += len(subfiles)
                    break  # Only count the first level

                # Add the tuple to the set of observations
                observations.add((subdirs_count, files_count))

    # Print unique observations
    for observation in observations:
        print(observation)


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