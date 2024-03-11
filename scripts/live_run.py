import os
import pandas as pd
import sys

sys.path.append(os.path.dirname(sys.path[0]))

from utils.InputUtils import InputUtils
from utils.Utils import Utils
from stages.LiveStages import LiveStages


def main():
    utils = Utils()
    input_utils = InputUtils()
    cli_inputs = input_utils.parse_command_inputs()

    stages = LiveStages(cli_inputs.input_path, cli_inputs.output_path, cli_inputs.dorado_path,
                        cli_inputs.model_path, cli_inputs.model_type, cli_inputs.last_k_predictions)

    print(stages.stage_separator)
    print("\nStarting Sturgeon Live Test Pipeline...\n")
    print(stages.stage_separator)

    print('Watching the following folder: {}\n'.format(cli_inputs.input_path))

    sturgeon_output_directory = ""
    existing_files_input_folder = set()
    while True:
        print("Waiting {} seconds for new sequencing reads (pod5 files)".format(cli_inputs.file_wait_time))
        new_files_input_folder, existing_files_input_folder = utils.new_file_checker(cli_inputs.input_path,
                                                                                     existing_files_input_folder,
                                                                                     cli_inputs.file_wait_time)

        if new_files_input_folder:
            '''
            converted_single_to_multi_read_fast5 = False
            if cli_inputs.single_to_multi_read_fast5:
                stages.convert_to_multi_read_fast5()
                converted_single_to_multi_read_fast5 = True

            if cli_inputs.convert_to_pod5:
                stages.convert_to_pod5(converted_single_to_multi_read_fast5)
            '''

            latest_bam_file_path = ""
            if cli_inputs.perform_basecalling:
                latest_bam_file_path = stages.live_basecalling_with_dorado(new_files_input_folder)

            stages.live_convert_bam_files_to_modkit_txt(latest_bam_file_path)
            stages.live_convert_modkit_txt_to_bed()
            sturgeon_output_directory = stages.run_sturgeon_predict()

        else:
            print("\nNo new sequencing read detected. Stopping execution...\n")
            print(stages.stage_separator)
            break

    if sturgeon_output_directory != "":
        output_csv = utils.get_latest_file(sturgeon_output_directory, extension='.csv')
        print("Output File: ", output_csv, "\n")
        output_df = pd.read_csv(output_csv)
        output_df = output_df.drop('number_probes', axis=1)
        max_column = output_df.apply(lambda row: row.idxmax(), axis=1)[0]
        max_score = output_df.max(axis=1)[0]
        print("Final Prediction: \n")
        print("Tumor Type: ", max_column)
        print("\nClassification Confidence Score: ", max_score)
        print(stages.stage_separator)

    print("\nCompleted Sturgeon Live Test Pipeline!!!\n")


if __name__ == "__main__":
    main()
