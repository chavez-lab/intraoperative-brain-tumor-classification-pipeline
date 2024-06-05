import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
sys.path.append(os.path.dirname(sys.path[0]))

from utils.InputUtils import InputUtils
from utils.Utils import Utils

file_writing_wait_time = 300


def run():
    utils = Utils()
    input_utils = InputUtils()
    cli_inputs = input_utils.get_file_transfer_pines_inputs()

    logging.info(utils.stage_separator)
    logging.info("\nStarting Files Transfer to Pines...\n")
    logging.info(utils.stage_separator)

    files_path = utils.get_target_directory_path(cli_inputs.local_files_path, 'pod5')
    pipeline_run_count = 0
    existing_files_input_folder = set()
    while True:
        if utils.new_file_checker(files_path, existing_files_input_folder, cli_inputs.wait_time):
            logging.info("Detected new pod5 files.")
            new_files_input_folder, existing_files_input_folder = utils.new_file_checker(files_path,
                                                                                         existing_files_input_folder,
                                                                                         file_writing_wait_time,
                                                                                         return_files=True)

            if new_files_input_folder:
                for file in new_files_input_folder:
                    if file != ".DS_Store":
                        new_file = files_path + "/" + file
                        logging.info(f'New file {str(new_file)}\n')
                        utils.scp_with_password(new_file, cli_inputs.remote_host, cli_inputs.remote_directory,
                                                cli_inputs.username, cli_inputs.password, cli_inputs.scp_timeout)

        elif pipeline_run_count < cli_inputs.max_wait_runs:
            pipeline_run_count += 1
        else:
            break

    logging.info(utils.stage_separator)
    logging.info("\nNo new sequencing read detected. Files Transfer to Pines Completed!!!\n")
    logging.info(utils.stage_separator)


if __name__ == "__main__":
    run()
