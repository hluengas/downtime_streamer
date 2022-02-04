from os import environ

STREAM_ADDRESS = environ.get("STREAM_ADDRESS")

EPISODE_PATH = environ.get("EPISODE_DIR")
BUMPER_PATH = environ.get("BUMPER_DIR")
META_PATH = environ.get("META_DIR")

PLAYLIST_PATH = META_PATH + "/ffmpeg_playlist.txt"
TREE_PATH = META_PATH + "/tree.txt"

SECTION_BREAK = "#########################################################################"

PLAYLIST_VIDEO_PATHS = [
    META_PATH + "/video_0.flv",
    META_PATH + "/video_1.flv",
    META_PATH + "/video_2.flv",
    META_PATH + "/video_3.flv",
]

PLAYLIST = [
    "file \'" + PLAYLIST_VIDEO_PATHS[0] + "\'\n",
    "file \'" + PLAYLIST_VIDEO_PATHS[1] + "\'\n",
    "file \'" + PLAYLIST_VIDEO_PATHS[2] + "\'\n",
    "file \'" + PLAYLIST_VIDEO_PATHS[3] + "\'\n"
]

FFPROBE_CMD = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
    ]

FFMPEG_STREAM_CMD = [
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

FFMPEG_TRANSCODE_BUMPER_CMD = [
    "ffmpeg",
    "-y",
    "-i",
    "INPUT_PATH",
    "-map",
    "0:v:0",
    "-map",
    "0:a:0",
    "-map",
    "-0:s",
    "-map_chapters",
    "-1",
    "-r",
    "24",
    "-g",
    "48",
    "-c:v",
    "libx264",
    "-profile:v",
    "high",
    "-preset",
    environ.get("VIDEO_ENCODER_PRESET"),
    "-tune",
    "animation",
    "-crf",
    "16",
    "-vf",
    "format=yuv420p,scale=1920:1080,setsar=1:1",
    "-c:a",
    "aac",
    "-filter:a",
    "volume=0.5",
    "-b:a",
    "320k",
    "-ar",
    "44100",
    "-ac",
    "2",
    "-f",
    "flv",
]

FFMPEG_TRANSCODE_EPISODE_CMD = [
    "ffmpeg",
    "-y",
    "-i",
    "INPUT_PATH",
    "-map",
    "0:v:0",
    "-map",
    "0:a:0",
    "-map",
    "-0:s",
    "-map_chapters",
    "-1",
    "-r",
    "24",
    "-g",
    "48",
    "-c:v",
    "libx264",
    "-profile:v",
    "high",
    "-preset",
    environ.get("VIDEO_ENCODER_PRESET"),
    "-tune",
    "animation",
    "-crf",
    "16",
    "-vf",
    "format=yuv420p,scale=1920:1080,setsar=1:1",
    "-c:a",
    "aac",
    "-filter:a",
    "volume=0.5",
    "-b:a",
    "320k",
    "-ar",
    "44100",
    "-ac",
    "2",
    "-f",
    "flv",
]



SERIES_WHITE_LIST = [
    "over.the.garden.wall",
    "archer.2009",
    "primal",
    "rick.and.morty",
    "avatar.the.last.airbender",
    "samurai.champloo",
    "batman.the.animated.series",
    "samurai.jack",
    "scooby.doo.where.are.you",
    "solar.opposites",
    "south.park",
    "brickleberry",
    "dragon.ball",
    "gravity.falls",
    "justice.league",
    "justice.league.unlimeted",
    "one.punch.man",
    "cowboy.bebop",
    "futurama",
    "harvey.birdman.atorney.at.law",
    "king.of.the.hill",
    "star.trek.lower.decks",
    "star.wars.the.clone.wars",
    "what.if",
]