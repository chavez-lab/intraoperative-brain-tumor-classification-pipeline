from Stages import *


def main():
    print("\nStarting Sturgeon Single Run Test Pipeline...\n")

    # Get input arguments
    utils = Utils()
    cli_inputs = utils.parse_command_inputs()

    # Execute stages of pipeline
    stages = Stages(cli_inputs.input_path, cli_inputs.output_path, cli_inputs.dorado_path)

    converted_single_to_multi_read_fast5 = False
    if cli_inputs.single_to_multi_read_fast5:
        stages.convert_to_multi_read_fast5()
        converted_single_to_multi_read_fast5 = True

    if cli_inputs.convert_to_pod5:
        stages.convert_to_pod5(converted_single_to_multi_read_fast5)

    if cli_inputs.perform_basecalling:
        if not cli_inputs.dorado_path:
            raise Exception("Please provide --dorado_path if you wish to perform basecalling.\n")
        stages.basecalling_with_dorado()

    stages.convert_bam_files_modkit()
    stages.convert_txt_to_bed()
    stages.run_sturgeon_predict()

    print("Completed Sturgeon Single Run Test Pipeline!!!\n")


if __name__ == "__main__":
    main()
