from sys import exit
from random import choice
from os import environ
from subprocess import Popen, PIPE
from time import sleep


def main():
    input_directory = environ.get("INPUT_DIR")
    tree_command = "tree -vnfio /tmp/tree.txt " + input_directory

    # use the linux tree command to recursively parse the directory structure
    process = Popen(tree_command.split(" "), stdout=PIPE)
    _output, _error = process.communicate()

    # read the tree output file into a list of video_filenames
    with open("/tmp/tree.txt") as open_file:
        all_filenames = open_file.readlines()

    # itterate through and keep only video_filenames ending in mkv or mp4
    video_filenames = []
    for file in all_filenames:
        path = file.strip("\n")

        if path[-4:] in [".mkv", ".mp4"]:
            video_filenames.append(path)

    ffmpeg_cmd = [
        "ffmpeg",
        "-i"
        "INPUT_PATH",
        "-map",
        "0:v:0",
        "-map",
        "0:a:0",
        "-framerate",
        environ.get("VIDEO_FRAMERATE"),
        "-c:v",
        "libx264",
        "-profile:v",
        "high",
        "-preset",
        environ.get("VIDEO_ENCODER_PRESET"),
        "-tune",
        "animation",
        "-crf",
        environ.get("VIDEO_ENCODER_CRF"),
        "-g",
        environ.get("VIDEO_ENCODER_KEYFRAME_INTERVAL"),
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

    for video_input_path in video_filenames:
        video_output_path = environ.get(
            "OUTPUT_DIR") + "/" + video_input_path.split("/")[-1]

        ffmpeg_cmd[2] = video_input_path
        ffmpeg_cmd[-1] = video_output_path
        transcode(ffmpeg_cmd)


def transcode(ffmpeg_cmd):
    sleep(5.0)
    print(ffmpeg_cmd)
    process = Popen(ffmpeg_cmd, stdout=PIPE)
    return(process.communicate())


if __name__ == "__main__":
    exit(main())
