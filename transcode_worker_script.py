from sys import argv
from subprocess import Popen, PIPE, STDOUT
from os.path import isdir
from constants import *


def main():

    # handle input parameters
    if len(argv) < 3:
        return
    episode_input_path = argv[0]
    index_to_prepare = argv[1]
    is_bumper = argv[2]

    # get video transcode output path
    video_output_path = PLAYLIST_VIDEO_PATHS[index_to_prepare]

    # choose ffmpeg parameters for episode vs bumpers (volume 50% for bumpers)
    if (is_bumper):
        ffmpeg_command = FFMPEG_TRANSCODE_BUMPER_CMD.copy()
    else:
        ffmpeg_command = FFMPEG_TRANSCODE_EPISODE_CMD.copy()

    # set input & output paths
    ffmpeg_command[3] = episode_input_path
    ffmpeg_command.append(video_output_path)

    # start ffmpeg
    ffmpeg_process = Popen(ffmpeg_command)
    (_output, _error) = ffmpeg_process.communicate()

    # get the duration and other metadata for the source video file
    write_metadata_json(video_output_path)


# create a json report of the media file's metadata
def write_metadata_json(content_path):

    # add input path to ffprobe command
    ffprobe_command = FFPROBE_JSON.copy()
    ffprobe_command.append(content_path)

    # run ffprobe, and wait for it to finish
    ffprobe_process = Popen(ffprobe_command, stdout=PIPE, universal_newlines=True)
    (output, _error) = ffprobe_process.communicate()

    # extract the video filename from its path
    media_filename = content_path.split("/")[-1]

    # output json file in the /meta/mediainfo path
    json_path = MEDIA_INFO_PATH + "/" + media_filename + ".json"

    # run ffprobe, and wait for it to finish
    if (not isdir(MEDIA_INFO_PATH)):
        mkdir_process = Popen(["mkdir", MEDIA_INFO_PATH])
        (_output, _error) = mkdir_process.communicate()

    # open and write the file
    with open(json_path, "w") as json_output_file:
        json_output_file.write(output)


if __name__ == "__main__":
    exit(main())
