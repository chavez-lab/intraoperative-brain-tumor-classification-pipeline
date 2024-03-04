import glob
import os
import argparse
import shutil
import time


class Utils:
    stage_separator = "\n##############################################################################################################\n"

    def __init__(self):
        pass

    def create_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"\nDirectory {path} created successfully\n")
        else:
            print(f"\nDirectory {path} already exists\n")

    def delete_directory(self, path):
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"\nDirectory {path} deleted successfully\n")
            except OSError:
                print(f"\nError while deleting {path}\n")
        else:
            print(f"\nDirectory {path} does not exist\n")

    def get_latest_file(self, path):
        all_files = os.listdir(path)
        files = [os.path.join(path, f) for f in all_files]
        if not files:
            return None
        latest_file = max(files, key=os.path.getmtime)
        return latest_file

    def delete_oldest_files(self, path, num_files_to_delete):
        all_files = os.listdir(path)
        files = [os.path.join(path, f) for f in all_files]
        files.sort(key=os.path.getmtime)
        files_to_delete = files[:num_files_to_delete]
        for file_to_delete in files_to_delete:
            try:
                os.remove(file_to_delete)
            except OSError:
                print("\nError while deleting old sturgeon output files.\n")

    def new_file_checker(self, input_folder_path, existing_files, wait_time):
        time.sleep(wait_time)
        current_files = set(os.listdir(input_folder_path))
        new_files = current_files - existing_files
        return new_files, current_files

    def copy_pod5_files_to_intermediate_folder(self, input_path, pod5_directory_path, new_files):
        # if previous set of pod5 files exist then delete them
        self.delete_directory(pod5_directory_path)

        # make a new pod5 files folder
        self.create_directory(pod5_directory_path)

        # copy newly added pod5 files to pod5 files folder
        new_files_paths = [input_path + "/" + new_file for new_file in new_files if new_file != ".DS_Store"]
        for new_files_path in new_files_paths:
            shutil.copy2(new_files_path, pod5_directory_path)

    def parse_command_inputs(self):
        # Parse inputs from the CLI command
        parser = argparse.ArgumentParser(prog="Sturgeon Pipeline",
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.set_defaults(func=lambda _: parser.print_help())

        parser.add_argument(
            "--input_path",
            type=str,
            required=True,
            help='Path to directory which contain nanopore sequencing reads (fast5/pod5 files)'
        )
        parser.add_argument(
            "--output_path",
            type=str,
            required=True,
            help='Path to directory where output of intermediate stages and final prediction output will be stored'
        )
        parser.add_argument(
            "--dorado_path",
            type=str,
            required=True,
            help='Path to directory where dorado is downloaded'
        )
        parser.add_argument(
            "--sturgeon_model_path",
            type=str,
            required=True,
            help='Path to directory where the Sturgeon model is downloaded'
        )
        parser.add_argument(
            '--single_to_multi_read_fast5',
            action='store_true',
            help='Set the flag to true to convert single-read fast5 files to multi-read fast5 files'
        )
        parser.add_argument(
            '--convert_to_pod5',
            action='store_true',
            help='Set the flag to true to convert fast5 files to pod5 files'
        )
        parser.add_argument(
            '--perform_basecalling',
            action='store_true',
            help='Set the flag to true to perform basecalling on pod5 files using Dorado'
        )
        parser.add_argument(
            '--file_wait_time',
            type=int,
            default=300,
            help='Set the sleep time between consecutive checks for new fast5 files (sequencing reads) in input folder'
        )
        parser.add_argument(
            '--last_k_predictions',
            type=int,
            default=1,
            help='Set the number of latest Sturgeon predictions (k) you wish to maintain in the output folder (saves last k Sturgeon predictions)'
        )

        args = parser.parse_args()
        return args

    def get_file_transfer_inputs(self):
        parser = argparse.ArgumentParser(prog="File transfer script",
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.set_defaults(func=lambda _: parser.print_help())
        parser.add_argument(
            "--input_path",
            type=str,
            required=True,
            help='Path to directory which contain nanopore sequencing reads (fast5 files)'
        )
        parser.add_argument(
            "--output_path",
            type=str,
            required=True,
            help='Path to directory in which fast5 files will be transferred and will serve as input folder for Sturgeon pipeline'
        )
        parser.add_argument(
            "--batch_size",
            type=int,
            default=1000,
            help='Number of files to be transferred in each batch'
        )
        parser.add_argument(
            "--wait_time",
            type=int,
            default=10,
            help='Wait time in seconds between each batch file transfer'
        )
        args = parser.parse_args()
        return args
