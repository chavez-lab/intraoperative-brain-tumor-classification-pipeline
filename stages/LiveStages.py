import os
import subprocess

from utils.Utils import Utils


class LiveStages:
    def __init__(self, input_path, output_path, dorado_path, sturgeon_model_path, sturgeon_model_type,
                 reference_genome_path, last_k_predictions):
        self.input_path = input_path
        self.output_path = output_path
        self.dorado_path = dorado_path
        self.sturgeon_model = sturgeon_model_path + "/" + sturgeon_model_type + ".zip"
        self.reference_genome_path = reference_genome_path
        self.utils = Utils()
        self.stage_separator = self.utils.stage_separator
        self.bam_file_count = 0
        self.modkit_file_count = 0
        self.bed_file_count = 0
        self.pod5_files_path = self.output_path + "/pod5_files/"
        self.bam_files_directory = self.output_path + "/bam_files/"
        self.modkit_files_directory = self.output_path + "/modkit_files/"
        self.bed_files_directory = self.output_path + "/bed_files/"
        self.sturgeon_output_directory = self.output_path + "/sturgeon_output/"
        self.sturgeon_max_output_count = last_k_predictions
        self.sturgeon_output_count = 0

    def live_basecalling_with_dorado(self, new_files):
        """
        Perform continuous basecalling on the set of new pod5 files (sequencing read) collected in the input folder
        after a certain wait time
        :param new_files:
        :return: a new bam file added to the intermediate bam_files_folder
        """

        pod5_folder_path = self.output_path + "/pod5_files/"
        self.utils.copy_pod5_files_to_intermediate_folder(self.input_path, pod5_folder_path, new_files)
        pod5_files_count = os.listdir(pod5_folder_path)

        print("Basecalling with Dorado on {} pod5 files...\n".format(pod5_files_count))
        # print("Downloading relevant models for Dorado")
        # subprocess.run([self.dorado_path, "download", "--model",
                        # "dna_r10.4.1_e8.2_400bps_hac@v4.1.0"], check=True)
        # subprocess.run([self.dorado_path, "download", "--model",
                        # "dna_r10.4.1_e8.2_400bps_hac@v4.1.0_5mCG_5hmCG@v2"], check=True)

        self.utils.create_directory(path=self.bam_files_directory)
        bam_files_path = self.bam_files_directory + "basecalled_" + str(self.bam_file_count) + ".bam"
        self.bam_file_count += 1

        basecall_cmd = " ".join([self.dorado_path, "basecaller", "hac,5mCG_5hmCG", pod5_folder_path, "--reference",
                                 self.reference_genome_path, ">", bam_files_path])
        subprocess.run(basecall_cmd, shell=True, check=True)

        print(self.stage_separator)
        return bam_files_path

    def live_convert_bam_files_to_modkit_txt(self, latest_bam_file_path):
        """
        Convert the latest bam file in the intermediate bam_files_folder to a modkit txt file
        :param latest_bam_file_path:
        :return: a new modkit txt file added to the intermediate modkit_files_directory
        """

        latest_bam_file = self.utils.get_latest_file(self.bam_files_directory, extension='.bam')

        print("Converting latest bam file(s) to txt files using Modkit...\n")

        self.utils.create_directory(self.modkit_files_directory)
        modkit_txt_files_path = self.modkit_files_directory + "modkit_" + str(self.modkit_file_count) + ".txt"
        self.modkit_file_count += 1

        subprocess.run(
            ["modkit", "extract", latest_bam_file, modkit_txt_files_path], check=True)

        print(self.stage_separator)

    def live_convert_modkit_txt_to_bed(self):
        """
        Convert all modkit files processed till now to a single bed file
        :return: single bed file in the intermediate bed_files_directory
        """

        print("Converting modkit txt files to bed files using inputtobed...\n")

        self.utils.delete_directory(self.bed_files_directory)
        self.utils.create_directory(self.bed_files_directory)

        subprocess.run(["sturgeon", "inputtobed", "-i", self.modkit_files_directory, "-o",
                        self.bed_files_directory, "-s", "modkit"], check=True)

        print(self.stage_separator)

    def run_sturgeon_predict(self):
        """
        Perform CNS tumor class classification using Sturgeon predict mode
        :return: plots and csv file containing classification confidence score
        """

        print("Running Sturgeon Predict...\n")

        subprocess.run(["sturgeon", "predict", "-i", self.bed_files_directory,
                        "-o", self.sturgeon_output_directory, "--model-files", self.sturgeon_model,
                        "--plot-results"], check=True)

        latest_files = self.utils.get_latest_files(self.sturgeon_output_directory, num_files=2)
        self.utils.rename_files(latest_files, self.sturgeon_output_count)
        self.sturgeon_output_count += 1

        # Maintain k latest sturgeon predictions in the output folder
        if len(os.listdir(self.sturgeon_output_directory)) > (self.sturgeon_max_output_count * 2):
            self.utils.delete_oldest_files(self.sturgeon_output_directory, num_files_to_delete=2)

        print(self.stage_separator)
        return self.sturgeon_output_directory
