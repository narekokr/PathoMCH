import os

def rename_subdirectories(base_dir, string_to_remove):
    for root, dirs, files in os.walk(base_dir, topdown=False):
        for name in dirs:
            new_name = name.replace(string_to_remove, '')
            if new_name != name:
                old_dir_path = os.path.join(root, name)
                new_dir_path = os.path.join(root, new_name)
                os.rename(old_dir_path, new_dir_path)
                print(f'Renamed: {old_dir_path} -> {new_dir_path}')

if __name__ == "__main__":
    base_dir = '/home/mahias/Downloads/gdc-client_v1.6.1_Ubuntu_x64/the_shit_so_far'
    string_to_remove = '_-_NO_MATCH'

    rename_subdirectories(base_dir, string_to_remove)
