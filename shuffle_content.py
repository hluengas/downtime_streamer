from pickle import NONE
from sys import exit
from random import choice, shuffle, sample
from os import environ
from os.path import isfile
from subprocess import run, Popen, PIPE, STDOUT
from time import sleep
from math import ceil, floor
from datetime import datetime

STREAM_ADDRESS = environ.get("STREAM_ADDRESS")

EPISODE_PATH = environ.get("EPISODE_DIR")
BUMPER_PATH = environ.get("BUMPER_DIR")
META_PATH = environ.get("META_DIR")

EPISODE_META_PATH = META_PATH + "/episode_"
BUMPER_META_PATH = META_PATH + "/bumper_"

HISTORY_PATH = META_PATH + "/already_played.txt"
PLAYLIST_PATH = META_PATH + "/ffmpeg_playlist.txt"
TREE_PATH = META_PATH + "/tree.txt"

FFMPEG_CMD = [
    "ffmpeg",
    "-f",
    "concat",
    "-safe",
    "0",
    "-re",
    "-stream_loop",
    "-1",
    "-i",
    PLAYLIST_PATH,
    "-c",
    "copy",
    "-f",
    "flv",
    STREAM_ADDRESS
]


PLAYLIST = [
    "file \'" + META_PATH + "/video_0.flv\'\n",
    "file \'" + META_PATH + "/video_1.flv\'\n",
    "file \'" + META_PATH + "/video_2.flv\'\n",
    "file \'" + META_PATH + "/video_3.flv\'\n"
]
VIDEO_DURATIONS = [0, 0, 0, 0]
VIDEO_PATHS = [
    "/tmp/content/episodes",
    "/tmp/content/episodes",
    "/tmp/content/episodes",
    "/tmp/content/episodes",
]
VIDEO_LINKS = [
    META_PATH + "/video_0.flv",
    META_PATH + "/video_1.flv",
    META_PATH + "/video_2.flv",
    META_PATH + "/video_3.flv",
]
COUNTER = 0


def main():
    global COUNTER

    # get a list of paths to all available episodes
    master_episode_list = parse_content_directory(EPISODE_PATH)
    master_bumper_list = parse_content_directory(BUMPER_PATH)

    # generate a random ordering of the epsiode list
    shuffed_episode_list = sample(master_episode_list, len(master_episode_list))
    shuffed_bumper_list = sample(master_bumper_list, len(master_bumper_list))

    # create the swap-chain playlsit: episode_a -> bumper_a -> episode_b -> bumper_b -> ... repeat...
    create_playlist_file()

    prepare_episode(shuffed_bumper_list, 0, -1)
    prepare_episode(shuffed_bumper_list, 1, -1)

    # start ffmpeg
    ffmpeg_process = Popen(FFMPEG_CMD, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    print("[FFMPEG Started!]\n")

    while(True):
        prepare_episode(shuffed_bumper_list, 2, 0)
        prepare_episode(shuffed_bumper_list, 3, 1)
        prepare_episode(shuffed_bumper_list, 0, 2)
        prepare_episode(shuffed_bumper_list, 1, 3)

    # end ffmpeg
    (_output, _error) = ffmpeg_process.communicate()


def prepare_episode(input_list, index_to_prepare, index_to_wait_on):
    global VIDEO_DURATIONS
    global VIDEO_PATHS
    global VIDEO_LINKS

    VIDEO_PATHS[index_to_prepare] = input_list.pop()
    VIDEO_DURATIONS[index_to_prepare] = get_media_duration(VIDEO_PATHS[index_to_prepare])
    symlink_video(VIDEO_PATHS[index_to_prepare], VIDEO_LINKS[index_to_prepare])
    print("#########################################################################")
    print("[Prepared Video]: " + str(index_to_prepare))
    print("[Source Path]: " + VIDEO_PATHS[index_to_prepare])
    print("[Linked To]: " + VIDEO_LINKS[index_to_prepare])
    print("[Duration]: " + str(VIDEO_DURATIONS[index_to_prepare]) + " seconds\n")

    if (index_to_wait_on == -1):
        print("[Skipping Wait]\n")
        return

    print("[Waiting For Video]: " + str(index_to_wait_on))
    print("[Duration]: " + str(VIDEO_DURATIONS[index_to_wait_on]))
    print("\n")
    sleep(VIDEO_DURATIONS[index_to_wait_on])
    return


def get_media_duration(content_path):
    ffprobe_command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        content_path
    ]
    # ffprobe
    ffprobe_process = Popen(ffprobe_command, stdout=PIPE)
    (output, error) = ffprobe_process.communicate()
    return(float(floor(float(output))))


# symlink episode
def symlink_video(episode_path, episode_link):
    link_command = [
        "ln",
        "-sf",
        episode_path,
        episode_link,
    ]
    link_process = Popen(link_command, stdout=PIPE)
    _output, _error = link_process.communicate()


def parse_content_directory(target_dir):

    # use the linux tree command to recursively parse the directory structure
    # using flags we will discard the tree characters and keep only the files/directory paths
    # the resulting list of all files & directoires is written to a text file
    tree_command = "tree -afUin -P *.flv -o " + TREE_PATH + " " + target_dir
    tree_process = Popen(tree_command.split(), stdout=PIPE)
    _output, _error = tree_process.communicate()

    # read the tree output file into a list of file paths
    with open(TREE_PATH) as in_file:
        all_filenames = in_file.read().splitlines()

    content_list = []

    # itterate through and keep only paths ending in ".flv"
    for path in all_filenames:
        if path[-4:] == ".flv":
            content_list.append(path)

    return content_list


def create_playlist_file():
    # check if the playlist file exists
    if (not isfile(PLAYLIST_PATH)):
        # if not create it
        touch_process = Popen(["touch", PLAYLIST_PATH], stdout=PIPE)
        touch_process.communicate()

    # write the ffmpeg_playlist to its file
    with open(PLAYLIST_PATH, 'w') as playlist_out_file:
        playlist_out_file.write("".join(PLAYLIST))


if __name__ == "__main__":
    exit(main())
