import os
import pandas as pd
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
sys.path.append(os.path.dirname(sys.path[0]))

from utils.InputUtils import InputUtils
from utils.Utils import Utils
from stages.LiveStages import LiveStages


def run():
    utils = Utils()
    input_utils = InputUtils()
    cli_inputs = input_utils.parse_command_inputs()

    stages = LiveStages(cli_inputs.input_path, cli_inputs.output_path, cli_inputs.dorado_path, cli_inputs.model_path,
                        cli_inputs.model_type, cli_inputs.reference_path, cli_inputs.modkit_path,
                        cli_inputs.last_k_predictions)

    logging.info(stages.stage_separator)
    logging.info("\nStarting Intraoperative Classification Pipeline...\n")
    logging.info(stages.stage_separator)

    logging.info('Watching the following folder for input: {}\n'.format(cli_inputs.input_path))

    sturgeon_output_directory = utils.empty_string
    existing_files_input_folder = set()
    while True:
        logging.info("Waiting {} seconds for new sequencing reads (pod5 files)".format(cli_inputs.file_wait_time))
        new_files_input_folder, existing_files_input_folder = utils.new_file_checker(cli_inputs.input_path,
                                                                                     existing_files_input_folder,
                                                                                     cli_inputs.file_wait_time)

        if new_files_input_folder:
            latest_bam_file_path = ""
            if cli_inputs.perform_basecalling:
                latest_bam_file_path = stages.live_basecalling_with_dorado(new_files_input_folder)

            stages.live_convert_bam_files_to_modkit_txt(latest_bam_file_path)
            stages.live_convert_modkit_txt_to_bed()
            sturgeon_output_directory = stages.run_sturgeon_predict()

        else:
            logging.info("\nNo new sequencing read detected. Stopping execution...\n")
            logging.info(stages.stage_separator)
            break

    if sturgeon_output_directory != utils.empty_string:
        output_csv = utils.get_latest_file(sturgeon_output_directory, extension='.csv')
        logging.info("Output File: ", output_csv, "\n")
        output_df = pd.read_csv(output_csv)
        output_df = output_df.drop('number_probes', axis=1)
        max_column = output_df.apply(lambda row: row.idxmax(), axis=1)[0]
        max_score = output_df.max(axis=1)[0]
        logging.info("Final Prediction: \n")
        logging.info("Tumor Type: ", max_column)
        logging.info("\nClassification Confidence Score: ", max_score)
        logging.info(stages.stage_separator)

    logging.info("\nCompleted Intraoperative Classification Pipeline!!!\n")


if __name__ == "__main__":
    run()
