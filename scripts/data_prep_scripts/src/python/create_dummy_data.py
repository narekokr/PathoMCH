import zipfile
import os

def create_dummy_structure_from_zip(zip_path, output_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for zip_info in zip_ref.infolist():
            # Derive the full path of the extracted file
            extracted_path = os.path.join(output_dir, zip_info.filename)

            if zip_info.filename.endswith('/'):
                # If it's a directory, create it
                os.makedirs(extracted_path, exist_ok=True)
            else:
                # If it's a file
                dir_name = os.path.dirname(extracted_path)
                os.makedirs(dir_name, exist_ok=True)

                # if os.path.basename(zip_info.filename) == "annotations.txt":
                #     # If it's the annotations.txt file, extract it with content
                if not os.path.basename(zip_info.filename).endswith(".svs"):
                    # if it is not a svs file, extract it with content
                    with zip_ref.open(zip_info.filename) as source, open(extracted_path, 'wb') as target:
                        target.write(source.read())
                else:
                    # Otherwise, create an empty file
                    with open(extracted_path, 'wb') as target:
                        pass

if __name__ == "__main__":
    zip_path = '/home/mathias/DSitLS/dsitls-project/scripts/data_prep_scripts/TCGA-COAD/bigData/DATA_CONTAINIG_SVS_FILES/files_unsorted.zip'  # Replace with your zip file path
    output_dir = '/home/mathias/DSitLS/dsitls-project/scripts/data_prep_scripts/TCGA-COAD/dummy_data'  # Replace with
    # the desired output directory
    create_dummy_structure_from_zip(zip_path, output_dir)
    print("done")