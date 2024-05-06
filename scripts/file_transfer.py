import os
import shutil
import time
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
sys.path.append(os.path.dirname(sys.path[0]))

from utils.InputUtils import InputUtils
from utils.Utils import Utils


def sort_key(file_name):
    parts = file_name.split("_")
    file_number = int(parts[-1].split(".")[0])
    return -file_number


def run():

    utils = Utils()
    input_utils = InputUtils()
    cli_inputs = input_utils.get_file_transfer_inputs()

    logging.info(utils.stage_separator)
    logging.info("\nStarting Files Transfer...\n")
    logging.info(utils.stage_separator)

    input_files = sorted(os.listdir(cli_inputs.input_path), key=sort_key)
    logging.info('\nFound {} files in {} folder\n'.format(len(input_files), cli_inputs.input_path))
    utils.create_directory(cli_inputs.output_path)
    logging.info(utils.stage_separator)

    while input_files:
        iters = min(len(input_files), cli_inputs.batch_size)
        for _ in range(iters):
            try:
                file = input_files.pop()
                file_path = os.path.join(cli_inputs.input_path, file)
                shutil.copy2(file_path, cli_inputs.output_path)
            except Exception as e:
                logging.info(e)
        logging.info("Transferred {} files, sleeping for {} seconds".format(iters, cli_inputs.wait_time))
        time.sleep(cli_inputs.wait_time)

    logging.info(utils.stage_separator)
    logging.info("\nFiles Transfer Completed!!!\n")
    logging.info(utils.stage_separator)


if __name__ == "__main__":
    run()
