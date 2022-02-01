from http.client import PROCESSING
from sys import exit
from os import environ
from os.path import exists
from subprocess import Popen, PIPE, STDOUT
from time import sleep

TREE_PATH = "/tmp/tree.txt"

INPUT_DIR = environ.get("INPUT_DIR")

FFMPEG_CMD = [
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
    "-r",
    "24",
    "-g",
    "48",
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
    "-vf",
    "format=yuv420p,scale=1920:1080,setsar=1:1",
    "-c:a",
    "aac",
    "-b:a",
    "320k",
    "-ar",
    "44100",
    "-ac",
    "2",
    "-f",
    "flv",
    "OUTPUT_PATH"
]
SECTION_BREAK = "#########################################################################"


def main():
    global FFMPEG_CMD

    video_paths = parse_content_directory(INPUT_DIR)
    print(video_paths)

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

        # set FFMPEG_CMD
        FFMPEG_CMD[3] = video_input_path
        FFMPEG_CMD[-1] = video_output_path_tmp
        print("FFMPEG COMMAND:")
        print(FFMPEG_CMD)

        # transcode video into .tmp file
        print("[TRANSCODING]: " + video_output_path_tmp)
        process = Popen(FFMPEG_CMD)
        _output, _error = process.communicate()

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

        # finished with episode
        print("[FINISHED]: " + video_output_path_flv)
        sleep(0.1)


def parse_content_directory(target_dir):

    # use the linux tree command to recursively parse the directory structure
    # using flags we will discard the tree characters and keep only the files/directory paths
    # the resulting list of all files & directoires is written to a text file
    tree_command = "tree -afUin -P *.flv -o " + TREE_PATH + " " + target_dir
    tree_process = Popen(tree_command.split())
    _output, _error = tree_process.communicate()
    print(TREE_PATH)
    print(target_dir)
    print(_output, _error)

    # read the tree output file into a list of file paths
    with open(TREE_PATH) as in_file:
        all_filenames = in_file.read().splitlines()

    content_list = []

    # itterate through and keep only paths ending in ".flv"
    for path in all_filenames:
        if path[-4:] in [".flv", ".mkv", ".mp4"]:
            content_list.append(path)

    return content_list


if __name__ == "__main__":
    exit(main())
