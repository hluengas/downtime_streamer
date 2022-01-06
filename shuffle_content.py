import sys, shutil, random, os
import subprocess

def main():
    content_path = "/temp"
    tree_command = "tree -vnfio tree.txt " + content_path
    filenames = []
    
    # use the linux tree command to recursively parse the directory structure
    process = subprocess.Popen(tree_command.split(), stdout=subprocess.PIPE)
    _output, _error = process.communicate()

    # read the tree output file into a list of filenames
    with open('tree.txt') as open_file:
        files = open_file.readlines()

    # itterate through and keep only filenames ending in mkv or mp4
    for file in files:
        path = file.strip('\n')

        if path[-4:] in [".mkv", ".mp4"]:
            filenames.append(path)

    ffmpeg_cmd_1 = """
        ffmpeg
        -re
"""
    ffmpeg_cmd_3 = """
            -map 0:v:0
            -map 0:a:0
            -map -0:s
            -framerate 24
            -c:v libx264
            -preset medium
            -crf 16
            -vf format=yuv420p
            -g 48
            -c:a aac
            -b:a 320k
            -ac 2
            -f flv
    """
    ffmpeg_cmd_4 = os.environ.get('STREAM_ADDRESS')

    ffmpeg_cmd_2 = "-i " + random.choice(filenames)
    ffmpeg_cmd = (ffmpeg_cmd_1 + ffmpeg_cmd_2 + ffmpeg_cmd_3 + ffmpeg_cmd_4)
    process = subprocess.Popen(ffmpeg_cmd.split(), stdout=subprocess.PIPE)
    print(filenames)
    print(ffmpeg_cmd.split())
    output, error = process.communicate()
    while (not error):
        ffmpeg_cmd_2 = "-i " + random.choice(filenames)
        ffmpeg_cmd = (ffmpeg_cmd_1 + ffmpeg_cmd_2 + ffmpeg_cmd_3 + ffmpeg_cmd_4)
        process = subprocess.Popen(ffmpeg_cmd.split(), stdout=subprocess.PIPE)
        print(filenames)
        print(ffmpeg_cmd.split())
        output, error = process.communicate()
    

if __name__ == '__main__': 
    sys.exit(main())