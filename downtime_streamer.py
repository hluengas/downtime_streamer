from cgitb import text
from sys import exit, stderr, stdout
from random import sample
from os.path import isfile
from subprocess import Popen, PIPE, STDOUT
from time import time, localtime, sleep

from constants import *

import asyncio
import json


def main():

    # get a list of paths to all available episodes
    master_episode_list = parse_content_directory(EPISODE_PATH, use_white_list=True)
    master_bumper_list = parse_content_directory(BUMPER_PATH)

    # generate a random ordering of the epsiode list
    shuffed_episode_list = sample(master_episode_list, len(master_episode_list))
    shuffed_bumper_list = sample(master_bumper_list, len(master_bumper_list))

    # create the log and the swap-chain playlist
    create_playlist_file(PLAYLIST, PLAYLIST_PATH)
    create_logfile(LOGFILE_PATH)

    get_media_json(shuffed_episode_list.pop())


# transcode the desired video, then
# symlink the output video to the desired link in the playlist swap-chain
def prepare_video(video_path, index_to_prepare, is_bumper=False, is_blocking=False):

    # get the duration of the video file
    video_duration = get_media_duration(video_path)

    # print debug info
    log_line(LOGFILE_PATH, ("[Preparing Video]: " + str(index_to_prepare)), section_break=True)
    log_line(LOGFILE_PATH, ("[Source Path]: " + video_path))
    log_line(LOGFILE_PATH, ("[Transcoding To]: " + PLAYLIST_VIDEO_PATHS[index_to_prepare]))
    log_line(LOGFILE_PATH, ("[Duration]: " + str(video_duration) + " seconds\n"))

    # transcode the desired video to the desired output video in the playlist swap-chain
    start_time = time()
    transcode_video(video_path, index_to_prepare, is_bumper, is_blocking)

    return (start_time, video_duration)


def get_media_json(content_path):
    # the FFPROBE command is tuned to only output the duration of the media in seconds
    # duplicate the command and append the desired path
    ffprobe_command = FFPROBE_JSON.copy()
    ffprobe_command.append(content_path)

    # run FFPROBE
    ffprobe_process = Popen(ffprobe_command, stdout=PIPE)
    (output, _error) = ffprobe_process.communicate()
    log_line(output)
    print(output)


# get the duration in seconds of the video at the given path
def get_media_duration(content_path):

    # the FFPROBE command is tuned to only output the duration of the media in seconds
    # duplicate the command and append the desired path
    ffprobe_command = FFPROBE_DURATION.copy()
    ffprobe_command.append(content_path)

    # run FFPROBE
    ffprobe_process = Popen(ffprobe_command, stdout=PIPE)
    (output, _error) = ffprobe_process.communicate()
    return(float(output))


# link the video at "episode_path" to the symbolic link at link_path"
def symlink_video(episode_path, link_path):

    # create link command
    # -s for soft/symbolic link
    # -f to force, overwriting existing symlinks
    link_command = [
        "ln",
        "-sf",
        episode_path,
        link_path,
    ]

    # link episode
    link_process = Popen(link_command, stdout=PIPE)
    (_output, _error) = link_process.communicate()


def transcode_video(episode_input_path, index_to_prepare, is_bumper=False, is_blocking=False):

    episode_output_path = PLAYLIST_VIDEO_PATHS[index_to_prepare]

    # choose ffmpeg parameters for episode vs bumpers
    if (is_bumper):
        ffmpeg_command = FFMPEG_TRANSCODE_BUMPER_CMD.copy()
    else:
        ffmpeg_command = FFMPEG_TRANSCODE_EPISODE_CMD.copy()

    # set input & output paths
    ffmpeg_command[3] = episode_input_path
    ffmpeg_command.append(episode_output_path)

    # start ffmpeg
    ffmpeg_process = Popen(ffmpeg_command, stdout=PIPE, stderr=STDOUT, universal_newlines=True)

    # this flag is used to halt the script until the video has finished transcoding
    if (is_blocking):
        log_line(LOGFILE_PATH, ("[Waiting For Transcoding To Finish]\n"))
        (_output, _error) = ffmpeg_process.communicate()
    else:
        log_line(LOGFILE_PATH, ("[Transcoding In Background]"))
        log_line(LOGFILE_PATH, ("[Waiting For Video]: " + str(index_to_prepare - 2)))


# get a list of paths to video content under a given target directory
def parse_content_directory(target_dir, use_white_list=False):

    # create the linux tree command to recursively parse the directory structure
    # using flags we will discard the tree characters and keep only the files/directory paths
    tree_command = [
        "tree",
        "-afUin",
        target_dir
    ]

    # run tree command
    tree_process = Popen(tree_command, stdout=PIPE, universal_newlines=True)
    (output, _error) = tree_process.communicate()

    # itterate through and keep only paths ending in ".mp4", ".mkv", or ".flv"
    content_list = []
    for path in output.splitlines():
        if path[-4:] in [".mp4", ".mkv", ".flv"]:

            # use whitelist to filter results
            if (use_white_list):
                for series in SERIES_WHITE_LIST:
                    if series in path:
                        content_list.append(path)
            else:
                content_list.append(path)

    return content_list


# create the logfile
def create_logfile(logfile_path):
    line = (SECTION_BREAK + str(localtime()) + "\n" + "[LOG STARTED]\n\n")
    with open(logfile_path, 'w') as logfile:
        logfile.write(line)


# add line to the logfile
def log_line(logfile_path, line, section_break=False, line_ending='\n'):
    if (section_break):
        with open(logfile_path, 'a') as logfile:
            logfile.write(SECTION_BREAK + line + line_ending)
    else:
        with open(logfile_path, 'a') as logfile:
            logfile.write(line + line_ending)

# create the swap-chain playlsit: episode_a -> bumper_a -> episode_b -> bumper_b -> ... repeat...
def create_playlist_file(playlist, playlist_path):
    # write the ffmpeg_playlist to its file
    with open(playlist_path, 'w') as playlist_out_file:
        playlist_out_file.write("".join(playlist))


if __name__ == "__main__":
    exit(main())
