from http.client import PROCESSING
from sys import exit
from random import choice
from os import environ
from os.path import exists
from subprocess import Popen, PIPE
from time import sleep


def main():
    input_directory = environ.get("INPUT_DIR")
    tree_command = "tree -vnfio /tmp/tree.txt " + input_directory

    # use the linux tree command to recursively parse the directory structure
    process = Popen(tree_command.split(" "), stdout=PIPE)
    _output, _error = process.communicate()

    # read the tree output file into a list of video_paths
    with open("/tmp/tree.txt") as open_file:
        all_filenames = open_file.readlines()

    # itterate through and keep only video_paths ending in mkv or mp4
    video_paths = []
    for file in all_filenames:
        path = file.strip("\n")

        if path[-4:] in [".mkv", ".mp4"]:
            video_paths.append(path)
            print(path)

    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-i",
        "INPUT_PATH",
        "-map",
        "0:v:0",
        "-map",
        "0:a:0",
        "-map",
        "-0:s",
        "-map_chapters",
        "-1",
        "-framerate",
        "24",
        "-c:v",
        "libx264",
        "-profile:v",
        "high",
        "-preset",
        environ.get("VIDEO_ENCODER_PRESET"),
        "-tune",
        "animation",
        "-crf",
        "16",
        "-g",
        "48",
        "-vf",
        "format=yuv420p,scale=1920:1080",
        "-c:a",
        "aac",
        "-b:a",
        "320k",
        "-ac",
        "2",
        "-f",
        "flv",
        "OUTPUT_PATH"
    ]

    for i, video_input_path in enumerate(video_paths):
        # set io paths
        print("PROCESSING: Video " + str(i+1) + " of " + str(len(video_paths)))
        video_filename = video_input_path.split("/")[-1][:-4].replace(" ", ".")
        video_output_path_flv = "".join([
            environ.get("OUTPUT_DIR"),
            "/",
            video_filename,
            ".flv"
        ])
        video_output_path_tmp = video_output_path_flv + ".tmp"
        print("FILENAME: " + video_filename)
        print("INPUT_PATH: " + video_input_path)
        print("TMP_PATH: " + video_output_path_tmp)
        print("FLV_PATH: " + video_output_path_flv)

        if exists(video_output_path_flv):
            print("FILE ALREADY EXISTS, SKIPPING...")
            continue
        sleep(1.0)

        # set ffmpeg_cmd
        ffmpeg_cmd[3] = video_input_path
        ffmpeg_cmd[-1] = video_output_path_tmp
        print("FFMPEG COMMAND:")
        print(ffmpeg_cmd)
        sleep(1.0)

        # transcode video into .tmp file
        print("[TRANSCODING]: " + video_output_path_tmp)
        process = Popen(ffmpeg_cmd, stdout=PIPE)
        _output, _error = process.communicate()
        sleep(1.0)

        # rename .tmp file into final .flv
        print("RENAMING")
        rename_cmd = [
            "mv",
            "-f",
            video_output_path_tmp,
            video_output_path_flv
        ]
        print(rename_cmd)
        process = Popen(rename_cmd, stdout=PIPE)
        _output, _error = process.communicate()
        sleep(1.0)

        # finished with episode
        print("[FINISHED]: " + video_output_path_flv)
        sleep(1.0)


if __name__ == "__main__":
    exit(main())
