from sys import exit
from random import choice, shuffle, sample
from os import environ
from os.path import isfile
from subprocess import Popen, PIPE
from time import sleep

STREAM_ADDRESS = environ.get("STREAM_ADDRESS")

CONTENT_PATH = environ.get("CONTENT_DIR")
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


def main():

    while(True):

        # get a list of paths to all available episodes
        master_episode_list = parse_content_directory(CONTENT_PATH)

        # generate a random ordering of the epsiode list
        shuffed_episode_list = sample(master_episode_list)

        # put into the format ffmpeg expects: (file '<filename>')
        ffmpeg_playlist = []
        for input_path in master_episode_list:
            if (input_path not in played_episodes):
                ffmpeg_playlist.append("file \'" + input_path + "\'")
            else:
                print("skipping episode... already played this session... ")

        # if the resulting playlist will be too short,
        # delete the play history and restart
        if (len(ffmpeg_playlist) < playlist_len):
            process = Popen(
                ["rm", "-f", HISTORY_PATH], stdout=PIPE)
            _output, _error = process.communicate()
            continue

        # check if list file exists
        if (not isfile(PLAYLIST_PATH)):
            # if not create it
            process = Popen(["touch", PLAYLIST_PATH], stdout=PIPE)
            print(process.communicate())

        # write the ffmpeg_playlist to its file
        with open(PLAYLIST_PATH, 'w') as playlist_out_file:
            for i in range(playlist_len):
                playlist_out_file.write(ffmpeg_playlist[i] + '\n')

        # write the files in the upcoming playlist to the play history
        with open(HISTORY_PATH, 'a') as out_file_play_history:
            for i in range(playlist_len):
                out_file_play_history.write(master_episode_list[i] + '\n')

        # debug log
        print("[###---INFO---###]")
        print(ffmpeg_playlist)
        print(FFMPEG_CMD)

        # start ffmpeg
        process = Popen(FFMPEG_CMD, stdout=PIPE)
        (output, error) = process.communicate()
        sleep(10.0)


def parse_content_directory(target_dir):

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


if __name__ == "__main__":
    exit(main())
