from os import environ

STREAM_ADDRESS = environ.get("STREAM_ADDRESS")

EPISODE_PATH = environ.get("EPISODE_DIR")
BUMPER_PATH = environ.get("BUMPER_DIR")
META_PATH = environ.get("META_DIR")

LOGFILE_PATH = META_PATH + "/downtime_streamer_log.txt"
PLAYLIST_PATH = META_PATH + "/ffmpeg_playlist.txt"

SECTION_BREAK = "#########################################################################\n"

PLAYLIST_VIDEO_PATHS = [
    META_PATH + "/video_0.flv",
    META_PATH + "/video_1.flv",
    META_PATH + "/video_2.flv",
    META_PATH + "/video_3.flv",
]

SOURCE_LINK_PATHS = [
    META_PATH + "/link_0",
    META_PATH + "/link_1",
    META_PATH + "/link_2",
    META_PATH + "/link_3",
]

PLAYLIST = [
    "file \'" + PLAYLIST_VIDEO_PATHS[0] + "\'\n",
    "file \'" + PLAYLIST_VIDEO_PATHS[1] + "\'\n",
    "file \'" + PLAYLIST_VIDEO_PATHS[2] + "\'\n",
    "file \'" + PLAYLIST_VIDEO_PATHS[3] + "\'\n"
]

FFPROBE_DURATION = [
    "ffprobe",
    "-v",
    "error",
    "-show_entries",
    "format=duration",
    "-of",
    "default=noprint_wrappers=1:nokey=1",
]

FFPROBE_JSON = [
    "ffprobe",
    "-show_format",
    "-show_streams",
    "-print_format",
    "json",
    "-loglevel",
    "quiet"
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
    "-loglevel",
    "verbose",
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
    "-map_metadata",
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
    "format=yuv420p,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:color=black,setsar=1:1",
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
    "-map_metadata",
    "-1",
    "-r",
    "24000/1001",
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
    "format=yuv420p,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:color=black,setsar=1:1",
    "-c:a",
    "aac",
    "-b:a",
    "320k",
    "-ar",
    "44100",
    "-ac",
    "2",
    "-f",
    "flv",
]

FFMPEG_TRANSCODE_JPN_EPISODE_CMD = [
    "ffmpeg",
    "-y",
    "-i",
    "INPUT_PATH",
    "-map",
    "0:v:0",
    "-map",
    "0:m:language:jpn",
    "-map",
    "-0:s",
    "-map_chapters",
    "-1",
    "-r",
    "24000/1001",
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
    "-filter_complex",
    "[0:v][0:s]overlay[v],format=yuv420p,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:-1:-1:color=black,setsar=1:1",
    "-c:a",
    "aac",
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
    "Batman.The.Animated.Series",
    "samurai.jack",
    "scooby.doo.where.are.you",
    "solar.opposites",
    "south.park",
    "brickleberry",
    "gravity.falls",
    "justice.league",
    "justice.league.unlimeted",
    "futurama",
    "harvey.birdman.atorney.at.law",
    "king.of.the.hill",
    "star.trek.lower.decks",
    "star.wars.the.clone.wars",
    "what.if",
]

JPN_LANG_LIST = [
    "samurai.champloo",
    "dragon.ball",
    "one.punch.man",
    "cowboy.bebop",
]
