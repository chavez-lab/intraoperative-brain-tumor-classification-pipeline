import os.path
import shutil
import subprocess

from Utils import Utils


class Stages:
    def __init__(self, input_path, output_path, dorado_path):
        self.input_path = input_path
        self.output_path = output_path
        self.dorado_path = dorado_path
        self.utils = Utils()
        self.stage_separator = self.utils.stage_separator
        self.bam_file_count = 0
        self.modkit_file_count = 0
        self.pod5_files_path = self.output_path + "/pod5_files/"
        self.bam_files_directory = self.output_path + "/bam_files/"
        self.modkit_files_directory = self.output_path + "/modkit_files/"
        self.bed_files_directory = self.output_path + "/bed_files/"

    def convert_to_multi_read_fast5(self):
        """
        Convert Single-read fast5 file obtained from Minion device to Multi-read fast5 file
        :return: Multi-read fast5 files
        """
        print(self.stage_separator)

        print("Converting single-read fast5 files to multi-read fast5 files...\n")
        multi_read_fast5_files_path = self.output_path + "/multi_read_fast5/"
        self.utils.create_directory(path=multi_read_fast5_files_path)

        subprocess.run(
            ["single_to_multi_fast5", "--input_path", self.input_path,
             "--save_path", multi_read_fast5_files_path], check=True)

        print(self.stage_separator)

    def convert_to_pod5(self, converted_single_to_multi_read_fast5):
        """
        Convert Multi-read fast5 files to pod5 files to be used for basecalling with Dorado
        :return: pod5 files
        """

        print("Converting multi-read fast5 files to pod5 files...\n")
        fast5_files_path = self.input_path
        if converted_single_to_multi_read_fast5:
            fast5_files_path = self.output_path + "/multi_read_fast5/"
        pod5_files_path = self.output_path + "/pod5/"
        self.utils.create_directory(path=pod5_files_path)

        subprocess.run(["pod5", "convert", "fast5", "--force-overwrite",
                        fast5_files_path, "--output", pod5_files_path], check=True)

        print(self.stage_separator)

    def basecalling_with_dorado(self):
        """
        Perform modified basecalling on pod5 files using ONT's Dorado basecaller.
        Download relevant models for basecalling.
        :return: bam files
        """

        print("Basecalling with Dorado on pod5 files...\n")
        print("Downloading relevant models for Dorado")
        subprocess.run([self.dorado_path, "download", "--model",
                        "dna_r10.4.1_e8.2_400bps_hac@v4.1.0"], check=True)
        subprocess.run([self.dorado_path, "download", "--model",
                        "dna_r10.4.1_e8.2_400bps_hac@v4.1.0_5mCG_5hmCG@v2"], check=True)

        pod5_files_path = self.output_path + "/dna_r10.4.1_e8.2_400bps_4khz/"
        bam_files_directory = self.output_path + "/test_outputs/"
        self.utils.create_directory(path=bam_files_directory)
        bam_files_path = bam_files_directory + "calls_4khz.bam"

        basecall_cmd = " ".join([self.dorado_path, "basecaller", "hac,5mCG_5hmCG", pod5_files_path, ">", bam_files_path])
        subprocess.run(basecall_cmd, shell=True, check=True)

        print(self.stage_separator)

    def convert_bam_files_modkit(self):
        """
        Convert bam files obtained from Dorado to txt files with methylation info using ONT's Modkit
        :return: txt files
        """

        print("Converting bam files to txt files using Modkit...\n")
        bam_files_path = self.output_path + "/test_outputs/calls_4khz.bam"
        txt_files_path = self.output_path + "/test_outputs/calls_4khz.txt"

        subprocess.run(
            ["modkit", "extract", bam_files_path, txt_files_path], check=True)

        print(self.stage_separator)

    def convert_txt_to_bed(self):
        """
        Convert txt files containing methylation info to bed files using inputtobed functionality of Sturgeon
        :return: bed files
        """

        print("Converting modkit txt files to bed files using inputtobed...\n")
        txt_files_path = self.output_path + "/test_outputs/calls_4khz.txt"
        bed_files_path = self.output_path + "/test_outputs/"

        subprocess.run(["sturgeon", "inputtobed", "-i", txt_files_path, "-o", bed_files_path, "-s", "modkit"],
                       check=True)

        print(self.stage_separator)

    def run_sturgeon_predict(self):
        """
        Perform CNS tumor class classification using Sturgeon predict mode
        :return: plots and csv file containing classification confidence score
        """

        print("Running Sturgeon Predict...\n")
        subprocess.run(["sturgeon", "predict", "-i", "/Users/chinmaysharma/Documents/sturgeon/demo/bed", "-o",
                        "/Users/chinmaysharma/Documents/sturgeon/demo/bed/results/", "--model-files",
                        "/Users/chinmaysharma/Documents/sturgeon/sturgeon/include/models/general.zip",
                        "--plot-results"], check=True)

        print(self.stage_separator)
