from cgitb import text
from os import popen
from sys import exit, stderr, stdout
from random import sample
from os.path import isfile, isdir
from subprocess import Popen, PIPE, STDOUT
from time import time, localtime, sleep

from constants import *

import json


def main():

    # get a list of paths to all available episodes
    master_episode_list = parse_content_directory(EPISODE_PATH, use_white_list=False)
    master_bumper_list = parse_content_directory(BUMPER_PATH)

    # generate a random ordering of the epsiode list
    shuffed_episode_list = sample(master_episode_list, len(master_episode_list))
    shuffed_bumper_list = sample(master_bumper_list, len(master_bumper_list))

    # create the log and the swap-chain playlist
    create_playlist_file(PLAYLIST, PLAYLIST_PATH)
    create_logfile(LOGFILE_PATH)

    # prep videos 1 & 2
    prepare_video(shuffed_episode_list.pop(), 0, is_blocking=True)
    prepare_video(shuffed_bumper_list.pop(), 1, is_blocking=True, is_bumper=True)

    # start ffmpeg
    ffmpeg_stream_process = Popen(FFMPEG_STREAM_CMD, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
    index_playing = 0
    log_line("[Stream Started!]\n", section_break=True)

    # prep video 3
    prepare_video(shuffed_episode_list.pop(), index_to_prepare)
    index_to_prepare = 3

    # while more shuffled content is available
    while(len(shuffed_episode_list) and len(shuffed_bumper_list)):
        # read ffmpeg stream debug output
        for line in ffmpeg_stream_process.stdout:
            # lines with "Statistics:" indicate the muxer has transitioned videos
            if("Statistics:" in line):
                # log
                log_line(line, section_break=True)
                log_line("[Detected Episode Change]")
                log_line("[Episode Completed]: " + str(index_playing) + "\n")

                # choose between episode and bumper
                # then start the transcoding process to prep the video
                if (index_to_prepare % 2):
                    prepare_video(shuffed_bumper_list.pop(), index_to_prepare, is_bumper=False)
                else:
                    prepare_video(shuffed_episode_list.pop(), index_to_prepare, is_bumper=True)

                # increment counters
                index_playing = (index_playing + 1) % 4
                index_to_prepare = (index_to_prepare + 1) % 4

# transcode the desired video
def prepare_video(video_path, index_to_prepare, is_bumper=False, is_blocking=False):

    # print debug info
    log_line(LOGFILE_PATH, ("[Preparing Video]: " + str(index_to_prepare)), section_break=True)
    log_line(LOGFILE_PATH, ("[Source Path]: " + video_path))
    log_line(LOGFILE_PATH, ("[Transcoding To]: " + PLAYLIST_VIDEO_PATHS[index_to_prepare]))

    # transcode the desired video to the desired output video in the playlist swap-chain
    transcode_video_cmd = [
        "python3",
        "transcode_worker_script.py",
        video_path,
        index_to_prepare,
        is_bumper
    ]
    transcoding_script = Popen(transcode_video_cmd)

    # if flag given, wait on worker script
    if (is_blocking):
        (_output, _error) = transcoding_script.communicate()


# get the duration in seconds of the video at the given path
def get_media_duration(content_path):

    # the FFPROBE command is tuned to only output the duration of the media in seconds
    # duplicate the command and append the desired path
    ffprobe_command = FFPROBE_DURATION.copy()
    ffprobe_command.append(content_path)

    # run FFPROBE
    ffprobe_process = Popen(ffprobe_command, stdout=PIPE, universal_newlines=True)
    (output, _error) = ffprobe_process.communicate()
    return(float(output))


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
