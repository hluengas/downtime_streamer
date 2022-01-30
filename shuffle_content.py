from sys import exit
from random import choice, shuffle, sample
from os import environ
from os.path import isfile
from subprocess import Popen, PIPE
from time import sleep

STREAM_ADDRESS = environ.get("STREAM_ADDRESS")

EPISODE_PATH = environ.get("EPISODE_DIR")
BUMPER_PATH = environ.get("BUMPER_DIR")
META_PATH = environ.get("META_DIR")

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
    "file 'episode_a.flv\'\n",
    "file 'bumper_a.flv\'\n",
    "file 'episode_b.flv\'\n",
    "file 'bumper_b.flv\'\n"
]


def main():

    # get a list of paths to all available episodes
    master_episode_list = parse_episode_directory(EPISODE_PATH)
    master_bumper_list = parse_bumper_directory(BUMPER_PATH)

    # generate a random ordering of the epsiode list
    shuffed_episode_list = sample(master_episode_list, len(master_episode_list))
    shuffed_bumper_list = sample(master_bumper_list, len(master_bumper_list))

    # create the swap-chain playlsit: episode_a -> bumper_a -> episode_b -> bumper_b -> ... repeat...
    create_playlist_file()

    # set initial linup
    episode_a = shuffed_episode_list.pop()
    bumper_a = shuffed_bumper_list.pop()
    symlink("a", episode_a, bumper_a)

    while(True):
        episode_a = shuffed_episode_list.pop()
        episode_b = shuffed_episode_list.pop()
        bumper_a = shuffed_bumper_list.pop()
        bumper_b = shuffed_bumper_list.pop()


    # start ffmpeg
    process = Popen(FFMPEG_CMD, stdout=PIPE)
    (output, error) = process.communicate()
    sleep(10.0)

def symlink(letter, episode, bumper):
    # symlink episode
    link_command = "ln -sf " + episode + "episode_"+ letter.lower() +".flv"
    process = Popen(link_command.split(), stdout=PIPE)
    _output, _error = process.communicate()

    # symlink bumper
    link_command = "ln -sf " + bumper + "bumper_"+ letter.lower() +".flv"
    process = Popen(link_command.split(), stdout=PIPE)
    _output, _error = process.communicate()


def parse_episode_directory(target_dir):

    # use the linux tree command to recursively parse the directory structure
    # using flags we will discard the tree characters and keep only the files/directory paths
    # the resulting list of all files & directoires is written to a text file
    tree_command = "tree -afUin -P *.flv -o " + TREE_PATH + " " + target_dir
    process = Popen(tree_command.split(), stdout=PIPE)
    _output, _error = process.communicate()

    # read the tree output file into a list of file paths
    with open(TREE_PATH) as in_file:
        all_filenames = in_file.read().splitlines()

    episode_list = []

    # itterate through and keep only paths ending in ".flv"
    for file in all_filenames:
        path = file
        if path[-4:] == ".flv":
            episode_list.append(path)

    return episode_list


def parse_bumper_directory(target_dir):

    # use the linux tree command to recursively parse the directory structure
    # using flags we will discard the tree characters and keep only the files/directory paths
    # the resulting list of all files & directoires is written to a text file
    tree_command = "tree -afUin -P *.flv -o " + TREE_PATH + " " + target_dir
    process = Popen(tree_command.split(), stdout=PIPE)
    _output, _error = process.communicate()

    # read the tree output file into a list of file paths
    with open(TREE_PATH) as in_file:
        all_filenames = in_file.read().splitlines()

    bumper_list = []

    # itterate through and keep only paths ending in ".flv"
    for file in all_filenames:
        path = file
        if path[-4:] == ".flv":
            bumper_list.append(path)

    return bumper_list


def create_playlist_file():
    # check if the playlist file exists
    if (not isfile(PLAYLIST_PATH)):
        # if not create it
        process = Popen(["touch", PLAYLIST_PATH], stdout=PIPE)
        print(process.communicate())

    # write the ffmpeg_playlist to its file
    with open(PLAYLIST_PATH, 'w') as playlist_out_file:
        playlist_out_file.write("".join(PLAYLIST))


if __name__ == "__main__":
    exit(main())
