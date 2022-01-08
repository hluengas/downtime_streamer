from sys import exit
from random import choice
from os import environ
from subprocess import Popen, PIPE
from time import sleep


def main():
    content_path = environ.get("CONTENT_DIR")
    print(content_path)
    tree_command = "tree -vnfio /tmp/tree.txt " + content_path
    video_filenames = []

    # use the linux tree command to recursively parse the directory structure
    process = Popen(tree_command.split(), stdout=PIPE)
    _output, _error = process.communicate()

    # read the tree output file into a list of video_filenames
    with open("/tmp/tree.txt") as open_file:
        all_filenames = open_file.readlines()

    whitelist = [
        "archer",
        "south.park",
        "rick.and.morty",
        "futurama",
        "brickleberry",
        "gravity.falls",
        "king.of.the.hill",
        "samurai.jack",
        "primal",
        "cowboy bebop",
        "justice.league",
        "one-punch.man",
        "over.the.garden.wall",
        "samurai.champloo",
        "scooby-doo",
        "solar.opposites"
    ]

    # itterate through and keep only video_filenames ending in mkv or mp4
    for file in all_filenames:
        print(file)
        path = file.strip("\n")

        if path[-4:] in [".mkv", ".mp4"]:
            for series in whitelist:
                if series in path.lower():
                    video_filenames.append(path)

    ffmpeg_cmd = [
        "ffmpeg",
        "-re",
        "-i",
        choice(video_filenames),
        "-map",
        "0:v:0",
        "-map",
        "0:a:0",
        "-map",
        "-0:s",
        "-map_metadata",
        "-1",
        "-framerate",
        environ.get("VIDEO_FRAMERATE"),
        "-c:v",
        "libx264",
        "-preset",
        environ.get("VIDEO_ENCODER_PRESET"),
        "-crf",
        environ.get("VIDEO_ENCODER_CRF"),
        "-vf",
        "format=yuv420p",
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
        environ.get("STREAM_ADDRESS"),
    ]
    print(video_filenames)
    print(ffmpeg_cmd)
    process = Popen(ffmpeg_cmd, stdout=PIPE)
    output, error = process.communicate()

    while not error:
        sleep(10)

        ffmpeg_cmd = [
            "ffmpeg",
            "-re",
            "-i",
            choice(video_filenames),
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-map",
            "-0:s",
            "-map_metadata",
            "-1",
            "-framerate",
            environ.get("VIDEO_FRAMERATE"),
            "-c:v",
            "libx264",
            "-preset",
            environ.get("VIDEO_AVC_PRESET"),
            "-crf",
            environ.get("VIDEO_ENCODER_CRF"),
            "-vf",
            "format=yuv420p",
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
            environ.get("STREAM_ADDRESS"),
        ]
        print(video_filenames)
        print(ffmpeg_cmd)
        process = Popen(ffmpeg_cmd, stdout=PIPE)
        output, error = process.communicate()

if __name__ == "__main__":
    exit(main())
