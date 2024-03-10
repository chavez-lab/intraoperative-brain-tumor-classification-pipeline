import argparse


class InputUtils:
    def __init__(self):
        pass

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
            "--model_path",
            type=str,
            required=True,
            help='Path to directory where the Sturgeon model is downloaded'
        )
        parser.add_argument(
            "--model_type",
            type=str,
            default="general",
            help='Select between general and brainstem sturgeon model'
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
