import os
import shutil
import time
import logging
import pexpect
import pandas as pd
import matplotlib.pyplot as plt

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

    def get_target_directory_path(self, input_folder_path, target_folder_name):
        try:
            for root, dirs, files in os.walk(input_folder_path):
                if target_folder_name in dirs:
                    return os.path.join(root, target_folder_name)
        except OSError as e:
            logging.info(f'Could not find pod5 folder, error: {e}\n')

        return None

    def scp_with_password(self, local_file, remote_host, remote_directory, username, password, timeout):
        scp_command = f'scp {local_file} {username}@{remote_host}:{remote_directory}'
        scp_process = pexpect.spawn(scp_command, timeout=timeout)

        try:
            logging.info(f'Starting file transfer of {str(local_file)}\n')
            scp_process.expect('password:')
            scp_process.sendline(password)
            scp_process.expect(pexpect.EOF)
            logging.info(f'{str(local_file)} transferred to pines successfully\n')
        except pexpect.EOF:
            logging.info('SCP process ended unexpectedly\n')
        except pexpect.TIMEOUT:
            logging.info('SCP process timed out\n')

    def generate_confidence_score_variation_plot(self, folder_path):
        dfs = []
        for file in os.listdir(folder_path):
            if file.endswith('.csv'):
                file_path = os.path.join(folder_path, file)
                df = pd.read_csv(file_path)
                dfs.append(df)

        combined_df = pd.concat(dfs, ignore_index=True)
        df = combined_df.drop(columns=['number_probes'])
        tumor_type = df.iloc[-1].idxmax()
        num_probes = combined_df['number_probes'].tolist()
        confidence_scores = combined_df[tumor_type].tolist()
        plt.plot(num_probes, confidence_scores, marker='o')
        plt.xlabel('Number of measured probes')
        plt.ylabel('Sturgeon Confidence Score')
        plt.title(tumor_type)
        plt.savefig(folder_path + 'confidence_score_vs_num_probes.png')
