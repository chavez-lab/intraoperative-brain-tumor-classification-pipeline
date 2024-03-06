from Utils import Utils
import subprocess


def main():
    utils = Utils()
    print(utils.get_latest_file("/Users/chinmaysharma/Documents/sturgeon/testing/test_results/bam_files/"))

    '''
    subprocess.run(
        ["python3", "/Users/chinmaysharma/Documents/sturgeon_pipeline/live_run.py", "--input_path",
         "/Users/chinmaysharma/Documents/sturgeon/testing/pod5_input", "--output_path", "/Users/chinmaysharma/Documents/sturgeon/testing/test_results",
         "--dorado_path", "/Users/chinmaysharma/Documents/dorado-0.5.3-osx-arm64/bin/dorado"],
        check=True)
    '''


if __name__ == "__main__":
    main()
