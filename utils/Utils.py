import os
import shutil
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class Utils:
    stage_separator = "\n##############################################################################################################\n"
    empty_string = ""

    def __init__(self):
        pass

    def create_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            logging.info(f"\nDirectory {path} created successfully\n")
        else:
            logging.info(f"\nDirectory {path} already exists\n")

    def delete_directory(self, path):
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                logging.info(f"\nDirectory {path} deleted successfully\n")
            except OSError:
                logging.error(f"\nError while deleting {path}\n")
        else:
            logging.info(f"\nDirectory {path} does not exist\n")

    def get_latest_file(self, path, extension):
        all_files = os.listdir(path)
        files = [os.path.join(path, f) for f in all_files if f.endswith(extension)]
        if not files:
            return None
        latest_file = max(files, key=os.path.getmtime)
        return latest_file

    def get_latest_files(self, path, num_files):
        all_files = os.listdir(path)
        files = [os.path.join(path, f) for f in all_files]
        files.sort(key=os.path.getmtime, reverse=True)
        latest_files = files[:num_files]
        return latest_files

    def delete_oldest_files(self, path, num_files_to_delete):
        all_files = os.listdir(path)
        files = [os.path.join(path, f) for f in all_files]
        files.sort(key=os.path.getmtime)
        files_to_delete = files[:num_files_to_delete]
        for file_to_delete in files_to_delete:
            try:
                os.remove(file_to_delete)
            except OSError:
                logging.error("\nError while deleting old sturgeon output files.\n")

    def new_file_checker(self, input_folder_path, existing_files, wait_time):
        time.sleep(wait_time)
        current_files = set(os.listdir(input_folder_path))
        new_files = current_files - existing_files
        return new_files, current_files

    def rename_files(self, files, file_num):
        for file in files:
            file_name, extension = os.path.splitext(file)
            file_name += "_" + str(file_num)
            new_file = file_name + extension
            try:
                os.rename(file, new_file)
            except OSError as e:
                logging.error(f"Following error occurred: {e}")

    def copy_pod5_files_to_intermediate_folder(self, input_path, pod5_directory_path, new_files):
        # if previous set of pod5 files exist then delete them
        self.delete_directory(pod5_directory_path)

        # make a new pod5 files folder
        self.create_directory(pod5_directory_path)

        # copy newly added pod5 files to pod5 files folder
        new_files_paths = [input_path + "/" + new_file for new_file in new_files if new_file != ".DS_Store"]
        for new_files_path in new_files_paths:
            shutil.copy2(new_files_path, pod5_directory_path)
