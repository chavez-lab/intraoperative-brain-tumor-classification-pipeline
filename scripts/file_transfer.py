import os
import shutil
import time
import sys

sys.path.append(os.path.dirname(sys.path[0]))

from utils.InputUtils import InputUtils
from utils.Utils import Utils


def run():

    utils = Utils()
    input_utils = InputUtils()
    cli_inputs = input_utils.get_file_transfer_inputs()

    print(utils.stage_separator)
    print("\nStarting Files Transfer...\n")
    print(utils.stage_separator)

    input_files = os.listdir(cli_inputs.input_path)
    print('\nFound {} files in {} folder\n'.format(len(input_files), cli_inputs.input_path))
    utils.create_directory(cli_inputs.output_path)
    print(utils.stage_separator)

    while input_files:
        iters = min(len(input_files), cli_inputs.batch_size)
        for _ in range(iters):
            try:
                file = input_files.pop()
                file_path = os.path.join(cli_inputs.input_path, file)
                shutil.copy2(file_path, cli_inputs.output_path)
            except Exception as e:
                print(e)
        print("Transferred {} files, sleeping for {} seconds".format(iters, cli_inputs.wait_time))
        time.sleep(cli_inputs.wait_time)

    print(utils.stage_separator)
    print("\nFiles Transfer Completed!!!\n")
    print(utils.stage_separator)


if __name__ == "__main__":
    run()
