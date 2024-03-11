import os
import shutil
import time

from utils.InputUtils import InputUtils
from utils.Utils import Utils


def main():
    print("\nStarting Files Transfer...\n")

    utils = Utils()
    input_utils = InputUtils()
    cli_inputs = input_utils.get_file_transfer_inputs()

    input_files = os.listdir(cli_inputs.input_path)
    print('\nFound {} files in {} folder\n'.format(len(input_files), cli_inputs.input_path))
    utils.create_directory(cli_inputs.output_path)

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

    print("\nFiles Transfer Completed!!!\n")


if __name__ == "__main__":
    main()
