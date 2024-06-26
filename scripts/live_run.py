import os
import pandas as pd
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
sys.path.append(os.path.dirname(sys.path[0]))

from utils.InputUtils import InputUtils
from utils.Utils import Utils
from stages.LiveStages import LiveStages

file_writing_wait_time = 300


def run():
    utils = Utils()
    input_utils = InputUtils()
    cli_inputs = input_utils.parse_command_inputs()
    files_path = utils.get_target_directory_path(cli_inputs.input_path, 'pod5')

    stages = LiveStages(files_path, cli_inputs.output_path, cli_inputs.dorado_path, cli_inputs.model_path,
                        cli_inputs.model_type, cli_inputs.reference_path, cli_inputs.modkit_path,
                        cli_inputs.last_k_predictions)

    logging.info(stages.stage_separator)
    logging.info("\nStarting Intraoperative Classification Pipeline...\n")
    logging.info(stages.stage_separator)

    logging.info('Watching the following folder for input: {}\n'.format(files_path))

    sturgeon_output_directory = utils.empty_string
    pipeline_run_count = 0
    existing_files_input_folder = set()
    while True:
        if utils.new_file_checker(files_path, existing_files_input_folder, cli_inputs.file_wait_time):
            logging.info("Detected new pod5 files.")
            new_files_input_folder, existing_files_input_folder = utils.new_file_checker(files_path,
                                                                                         existing_files_input_folder,
                                                                                         file_writing_wait_time,
                                                                                         return_files=True)

            if new_files_input_folder:
                latest_bam_file_path = ""
                if cli_inputs.perform_basecalling:
                    latest_bam_file_path = stages.live_basecalling_with_dorado(new_files_input_folder)

                stages.live_convert_bam_files_to_modkit_txt(latest_bam_file_path)
                stages.live_convert_modkit_txt_to_bed()
                sturgeon_output_directory = stages.run_sturgeon_predict()
                pipeline_run_count = 0

        elif pipeline_run_count < cli_inputs.max_wait_runs:
            pipeline_run_count += 1
        else:
            logging.info("\nNo new sequencing read detected. Stopping execution...\n")
            logging.info(stages.stage_separator)
            break

    if sturgeon_output_directory != utils.empty_string:
        output_csv = utils.get_latest_file(sturgeon_output_directory, extension='.csv')
        logging.info(f"\nOutput File: {output_csv} \n")
        output_df = pd.read_csv(output_csv)
        output_df = output_df.drop('number_probes', axis=1)
        max_column = output_df.apply(lambda row: row.idxmax(), axis=1)[0]
        max_score = output_df.max(axis=1)[0]
        logging.info("\nFinal Prediction: \n")
        logging.info(f"\nTumor Type: {max_column} \n")
        logging.info(f"\nClassification Confidence Score: {max_score} \n")
        logging.info(stages.stage_separator)
        utils.generate_confidence_score_variation_plot(sturgeon_output_directory)

    logging.info("\nCompleted Intraoperative Classification Pipeline!!!\n")


if __name__ == "__main__":
    run()
