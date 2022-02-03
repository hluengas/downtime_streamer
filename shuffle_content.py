from sys import exit
from random import sample
from os import environ
from os.path import isfile
from subprocess import Popen, PIPE, STDOUT
from time import sleep


STREAM_ADDRESS = environ.get("STREAM_ADDRESS")

EPISODE_PATH = environ.get("EPISODE_DIR")
BUMPER_PATH = environ.get("BUMPER_DIR")
META_PATH = environ.get("META_DIR")

PLAYLIST_PATH = META_PATH + "/ffmpeg_playlist.txt"
TREE_PATH = META_PATH + "/tree.txt"

SECTION_BREAK = "#########################################################################"

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

    while(True):
        COUNTER = 0

        # get a list of paths to all available episodes
        master_episode_list = parse_content_directory(EPISODE_PATH)
        master_bumper_list = parse_content_directory(BUMPER_PATH)

        # generate a random ordering of the epsiode list
        shuffed_episode_list = sample(master_episode_list, len(master_episode_list))
        shuffed_bumper_list = sample(master_bumper_list, len(master_bumper_list))

        # create the swap-chain playlsit: episode_a -> bumper_a -> episode_b -> bumper_b -> ... repeat...
        create_playlist_file()

        # prepare first video file
        index_playing = -1
        index_to_prepare = 0
        prepare_episode(shuffed_episode_list.pop(), index_to_prepare)
        index_to_prepare = index_to_prepare + 1

        # start ffmpeg
        ffmpeg_process = Popen(FFMPEG_CMD, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
        print(SECTION_BREAK)
        print("[FFMPEG Started!]\n")

        while(len(shuffed_episode_list) and len(shuffed_bumper_list)):

            for line in ffmpeg_process.stdout:
                if("[flv @" in line):
                    print(SECTION_BREAK)
                    print(line, end="")
                    print("[Detected Episode Change]")
                    print("[Episode Completed]: " + str(index_playing) + "\n")

                    if (index_to_prepare % 2):
                        prepare_episode(shuffed_bumper_list.pop(), index_to_prepare)
                    else:
                        prepare_episode(shuffed_episode_list.pop(), index_to_prepare)

                    index_playing = (index_playing + 1) % 4
                    index_to_prepare = (index_to_prepare + 1) % 4

        # end ffmpeg
        sleep(get_media_duration(VIDEO_PATHS[index_playing]) + get_media_duration(VIDEO_PATHS[index_to_prepare]))
        ffmpeg_process.terminate()


def prepare_episode(input_path, index_to_prepare):
    global VIDEO_DURATIONS
    global VIDEO_PATHS
    global VIDEO_LINKS

    VIDEO_PATHS[index_to_prepare] = input_path
    VIDEO_DURATIONS[index_to_prepare] = get_media_duration(VIDEO_PATHS[index_to_prepare])
    symlink_video(VIDEO_PATHS[index_to_prepare], VIDEO_LINKS[index_to_prepare])
    print(SECTION_BREAK)
    print("[Prepared Video]: " + str(index_to_prepare))
    print("[Source Path]: " + VIDEO_PATHS[index_to_prepare])
    print("[Linked To]: " + VIDEO_LINKS[index_to_prepare])
    print("[Duration]: " + str(VIDEO_DURATIONS[index_to_prepare]) + " seconds\n")
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
    return(float(output))


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
