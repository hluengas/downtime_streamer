from sys import exit
from random import choice,shuffle
from os import environ
from subprocess import Popen, PIPE
from time import sleep


def main():

    while(True):

        input_video_paths = get_content_paths()
        playlist = []

        for input_path in input_video_paths:
            playlist.append("file \'" + input_path + "\'\n")

        shuffle(playlist)

        with open('/tmp/playlist.txt', 'w') as writer:
            writer.writelines(playlist)
            writer.close()

        ffmpeg_cmd = [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-re",
            "-i",
            "/tmp/playlist.txt",
            "-c",
            "copy",
            "-f",
            "flv",
            environ.get("STREAM_ADDRESS")
        ]

        sleep(1.0)
        print(ffmpeg_cmd)
        process = Popen(ffmpeg_cmd, stdout=PIPE)
        (output, error) = process.communicate()


def get_content_paths():
    input_video_paths = []

    content_path = environ.get("CONTENT_DIR")
    tree_command = "tree -vnfio /tmp/tree.txt " + content_path

    # use the linux tree command to recursively parse the directory structure
    process = Popen(tree_command.split(), stdout=PIPE)
    _output, _error = process.communicate()

    # read the tree output file into a list of input_video_paths
    with open("/tmp/tree.txt") as open_file:
        all_filenames = open_file.readlines()

    # itterate through and keep only input_video_paths ending in mkv or mp4
    for file in all_filenames:
        path = file.strip("\n")
        if path[-4:] == ".flv":
            input_video_paths.append(path)

    return input_video_paths


if __name__ == "__main__":
    exit(main())
