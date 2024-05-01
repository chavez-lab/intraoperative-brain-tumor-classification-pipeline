# Intraoperative CNS tumor classification pipeline

Clone this repository to make the pipeline available on local system:
```commandline
git clone https://github.com/chavez-lab/intraoperative-brain-tumor-classification-pipeline.git
```

Run setup.py file to install custom packages:
```commandline
cd intraoperative-brain-tumor-classification-pipeline
python3 setup.py install
```

Command to run the pipeline:
```commandline
python3 <path_to_scripts_directory>/live_run.py \
--input_path <path_to_pod5_files_on_local_system> \
--output_path <path_to_output_folder_on_local_system> \
--dorado_path <path_to_dorado_basecaller_on_local_system> \
--model_path <path_to_folder_containing_model> \
--model_type <general_or_brainstem> \
--reference_path <path_to_chm13v2.0.fa.gz_file> \
--modkit_path <path_to_modkit_on_local_system> \
--perform_basecalling \
--file_wait_time <wait_time_in_seconds> \
--last_k_predictions <integer_value>
```

Command to get help for input arguments:
```commandline
python3 <path_to_pipeline_directory>/live_run.py --help
```