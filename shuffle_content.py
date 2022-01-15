from sys import exit
from random import choice
from os import environ
from subprocess import Popen, PIPE
from time import sleep


def main():
    content_path = environ.get("CONTENT_DIR")
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
        "cowboy.bebop",
        "justice.league",
        "one-punch.man",
        "over.the.garden.wall",
        "samurai.champloo",
        "scooby-doo",
        "solar.opposites",
        "avatar.the.last.airbender",
        "batman.the.animated.series",
        "dragon.ball",
        "harvey.birdman.attorney.at.law"
    ]

    # itterate through and keep only video_filenames ending in mkv or mp4
    for file in all_filenames:
        path = file.strip("\n")

        if path[-4:] in [".mkv", ".mp4"]:
            for series in whitelist:
                if series in path.lower().replace(" ", "."):
                    video_filenames.append(path)

    ffmpeg_cmd_1 = [
        "ffmpeg",
        "-re",
        "-i"
    ]

    ffmpeg_cmd_2 = [
        "-map",
        "0:v:0",
        "-map",
        "0:a:0",
        "-framerate",
        environ.get("VIDEO_FRAMERATE"),
        "-c:v",
        "libx264",
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
        environ.get("STREAM_ADDRESS")
    ]

    ffmpeg_cmd = ffmpeg_cmd_1 + [choice(video_filenames)] + ffmpeg_cmd_2
    (output, error) = play_random(ffmpeg_cmd)

    while (not error):
        ffmpeg_cmd = ffmpeg_cmd_1 + [choice(video_filenames)] + ffmpeg_cmd_2
        (output, error) = play_random(ffmpeg_cmd)


def play_random(ffmpeg_cmd):
    sleep(5.0)
    print(ffmpeg_cmd)
    process = Popen(ffmpeg_cmd, stdout=PIPE)
    return(process.communicate())


if __name__ == "__main__":
    exit(main())
