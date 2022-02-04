from cgitb import text
from sys import exit, stderr, stdout
from random import sample
from os.path import isfile
from subprocess import Popen, PIPE, STDOUT
from time import sleep
from constants import *


def main():

    # get a list of paths to all available episodes
    master_episode_list = parse_content_directory(EPISODE_PATH, use_white_list=True)
    master_bumper_list = parse_content_directory(BUMPER_PATH)

    # generate a random ordering of the epsiode list
    shuffed_episode_list = sample(master_episode_list, len(master_episode_list))
    shuffed_bumper_list = sample(master_bumper_list, len(master_bumper_list))

    # create the swap-chain playlsit: episode_a -> bumper_a -> episode_b -> bumper_b -> ... repeat...
    create_playlist_file(PLAYLIST, PLAYLIST_PATH)

    # prepare first video file
    index_playing = -1
    index_to_prepare = 0
    prepare_video(shuffed_episode_list.pop(), index_to_prepare, is_bumper=False, is_blocking=True)
    index_to_prepare = index_to_prepare + 1

    # prepare second video file
    prepare_video(shuffed_bumper_list.pop(), index_to_prepare, is_bumper=True, is_blocking=True)
    index_to_prepare = index_to_prepare + 1

    # start ffmpeg
    ffmpeg_stream_process = Popen(FFMPEG_STREAM_CMD, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
    print(SECTION_BREAK)
    print("[Stream Started!]\n")

    playlist_video_durations = [
        0.0,
        0.0,
        0.0,
        0.0,
    ]

    # while there is still content
    while(len(shuffed_episode_list) and len(shuffed_bumper_list)):

        # read ffmpeg stream debug output
        for line in ffmpeg_stream_process.stdout:

            # lines with "Statistics:" indicate the muxer has transitioned videos
            if("Statistics:" in line):

                # print debug
                print(SECTION_BREAK)
                print(line, end="")
                print("[Detected Episode Change]")
                print("[Episode Completed]: " + str(index_playing) + "\n")

                # choose between episode and bumper
                # then start the transcoding process to prep the video
                if (index_to_prepare % 2):
                    playlist_video_durations[index_to_prepare] = prepare_video(shuffed_bumper_list.pop(), index_to_prepare, is_bumper=False)
                else:
                    playlist_video_durations[index_to_prepare] = prepare_video(shuffed_episode_list.pop(), index_to_prepare, is_bumper=True)

                # increment counters
                index_playing = (index_playing + 1) % 4
                index_to_prepare = (index_to_prepare + 1) % 4

    # wait for prepared epsiodes to finish
    sleep(playlist_video_durations[index_playing] + playlist_video_durations[index_to_prepare])
    # terminate FFMPEG to stop it looping
    ffmpeg_stream_process.terminate()


# transcode the desired video, then
# symlink the output video to the desired link in the playlist swap-chain
def prepare_video(video_path, index_to_prepare, is_bumper=False, is_blocking=False):

    # get the duration of the video file
    video_duration = get_media_duration(video_path)

    # print debug info
    print(SECTION_BREAK)
    print("[Preparing Video]: " + str(index_to_prepare))
    print("[Source Path]: " + video_path)
    print("[Transcoding To]: " + PLAYLIST_VIDEO_PATHS[index_to_prepare])
    print("[Duration]: " + str(video_duration) + " seconds\n")

    # transcode the desired video to the desired output video in the playlist swap-chain
    transcode_video(video_path, PLAYLIST_VIDEO_PATHS[index_to_prepare], is_bumper, is_blocking)

    return video_duration


# get the duration in seconds of the video at the given path
def get_media_duration(content_path):

    # the FFPROBE command is tuned to only output the duration of the media in seconds
    # duplicate the command and append the desired path
    ffprobe_command = FFPROBE_CMD.copy()
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


def transcode_video(episode_input_path, episode_output_path, is_bumper=False, is_blocking=False):

    # choose ffmpeg parameters for episode vs bumpers
    if (is_bumper):
        ffmpeg_command = FFMPEG_TRANSCODE_BUMPER_CMD.copy()
    else:
        ffmpeg_command = FFMPEG_TRANSCODE_EPISODE_CMD.copy()

    # # choose eng vs jpn language path
    # if (use_jpn_lang):
    #     ffmpeg_command = FFMPEG_TRANSCODE_JPN_EPISODE_CMD.copy()
    #     # ffmpeg_command[27] = str(ffmpeg_command[27]).replace("subtitles=video.mkv", ("subtitles=" + str(episode_input_path)))
    # else:
    #     ffmpeg_command = FFMPEG_TRANSCODE_EPISODE_CMD.copy()

    # set input & output paths
    ffmpeg_command[3] = episode_input_path
    ffmpeg_command.append(episode_output_path)

    # start ffmpeg
    ffmpeg_process = Popen(ffmpeg_command, stdout=PIPE, stderr=STDOUT, universal_newlines=True)

    # this flag is used to halt the script until the video has finished transcoding
    if (is_blocking):
        print("[Waiting For Transcoding To Finish]\n")
        (_output, _error) = ffmpeg_process.communicate()
    else:
        print("[Transcoding In Background]")


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
                for series in JPN_LANG_LIST:
                    if series in path:
                        content_list.append(path)
            else:
                content_list.append(path)

    return content_list


# create the swap-chain playlsit: episode_a -> bumper_a -> episode_b -> bumper_b -> ... repeat...
def create_playlist_file(playlist, playlist_path):

    # check if the playlist file exists
    if (not isfile(playlist_path)):
        # if not create it
        touch_process = Popen(["touch", playlist_path], stdout=PIPE)
        touch_process.communicate()

    # write the ffmpeg_playlist to its file
    with open(playlist_path, 'w') as playlist_out_file:
        playlist_out_file.write("".join(playlist))


if __name__ == "__main__":
    exit(main())
