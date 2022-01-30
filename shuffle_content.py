from pickle import NONE
from sys import exit
from random import choice, shuffle, sample
from os import environ
from os.path import isfile
from subprocess import run, Popen, PIPE, STDOUT
from time import sleep
from math import ceil
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
    "-i",
    PLAYLIST_PATH,
    "-c",
    "copy",
    "-f",
    "flv",
    STREAM_ADDRESS
]


PLAYLIST = [
    "file \'" + META_PATH + "/episode_a.flv\'\n",
    "file \'" + META_PATH + "/bumper_a.flv\'\n",
    "file \'" + META_PATH + "/episode_b.flv\'\n",
    "file \'" + META_PATH + "/bumper_b.flv\'\n"
]


def main():

    # get a list of paths to all available episodes
    master_episode_list = parse_content_directory(EPISODE_PATH)
    master_bumper_list = parse_content_directory(BUMPER_PATH)

    # generate a random ordering of the epsiode list
    shuffed_episode_list = sample(
        master_episode_list, len(master_episode_list))
    shuffed_bumper_list = sample(master_bumper_list, len(master_bumper_list))

    # create the swap-chain playlsit: episode_a -> bumper_a -> episode_b -> bumper_b -> ... repeat...
    create_playlist_file()

    # set initial lineup
    current_episode_letter = "a"
    next_episode_letter = "b"

    # get next episode & bumper
    episode = shuffed_episode_list.pop()
    bumper = shuffed_bumper_list.pop()

    # link next episode & bumpers
    symlink_episode(current_episode_letter, episode)
    symlink_bumper(current_episode_letter, bumper)

    # swap current & next
    temp = current_episode_letter
    current_episode_letter = next_episode_letter
    next_episode_letter = temp

    # get wait time
    episode_wait_time = get_media_duration(episode)
    bumper_wait_time = get_media_duration(bumper)

    # start ffmpeg
    ffmpeg_process = Popen(FFMPEG_CMD, stdout=PIPE,
                           stderr=PIPE, universal_newlines=True)

    while(len(shuffed_episode_list) and len(shuffed_bumper_list)):

        # get next episode & bumper
        episode = shuffed_episode_list.pop()
        bumper = shuffed_bumper_list.pop()

        # link next episode & bumpers
        symlink_episode(current_episode_letter, episode)
        # wait for episode completion
        print(episode_wait_time)
        sleep(episode_wait_time)

        # link next episode & bumpers
        symlink_bumper(current_episode_letter, bumper)
        # wait for episode completion
        print(bumper_wait_time)
        sleep(bumper_wait_time)

        # swap current & next
        temp = current_episode_letter
        current_episode_letter = next_episode_letter
        next_episode_letter = temp

        # get next wait time
        # get wait time
        episode_wait_time = get_media_duration(episode)
        bumper_wait_time = get_media_duration(bumper)

    # end ffmpeg
    (_output, _error) = ffmpeg_process.communicate()


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
    return(float(output))


def symlink_episode(letter, episode):
    print("[LETTER]: " + letter.lower())

    # symlink episode
    link_command = "ln -sf " + episode + " " + \
        EPISODE_META_PATH + letter.lower() + ".flv"
    print(link_command)
    link_process = Popen(link_command.split(), stdout=PIPE)
    _output, _error = link_process.communicate()

def symlink_bumper(letter, bumper):
    print("[LETTER]: " + letter.lower())

    # symlink bumper
    link_command = "ln -sf " + bumper + " " + BUMPER_META_PATH + letter.lower() + \
        ".flv"
    print(link_command)
    link_process = Popen(link_command.split(), stdout=PIPE)
    _output, _error = link_process.communicate()


def parse_content_directory(target_dir):

    # use the linux tree command to recursively parse the directory structure
    # using flags we will discard the tree characters and keep only the files/directory paths
    # the resulting list of all files & directoires is written to a text file
    tree_command = "tree -afUin -P *.flv -o " + TREE_PATH + " " + target_dir
    print(tree_command)
    tree_process = Popen(tree_command.split(), stdout=PIPE)
    _output, _error = tree_process.communicate()

    # read the tree output file into a list of file paths
    with open(TREE_PATH) as in_file:
        all_filenames = in_file.read().splitlines()

    content_list = []

    # itterate through and keep only paths ending in ".flv"
    for file in all_filenames:
        path = file
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
