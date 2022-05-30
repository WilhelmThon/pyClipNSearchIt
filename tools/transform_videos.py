import sys
import os
import platform
import subprocess

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from src import logger
from src import util
from src.arguments import _is_valid_input
from src.hasher import preprocess

def get_valid_output(path: str):
    abs_path = os.path.abspath(path)

    if os.path.isfile(abs_path):
        raise TypeError("The output path cannot be a file") 

    os.makedirs(abs_path, exist_ok=True)

    return abs_path

def get_converters():
    system_name = platform.system()

    if system_name == 'Windows':
        converter = os.path.join(util.ROOT_DIR, "ffmpeg.exe")
    elif system_name == 'Linux':
        converter = "ffmpeg"

    converters = []
    
    converters.append((f"{converter} -nostdin -y -v 0 -vsync passthrough -i \"{{}}\" -vf \"pad=width=ceil(iw/2)*2:height=ceil(ih/2)*2,eq=brightness=0.25\" \"{{}}\"", "brightness_high"))
    converters.append((f"{converter} -nostdin -y -v 0 -vsync passthrough -i \"{{}}\" -vf \"pad=width=ceil(iw/2)*2:height=ceil(ih/2)*2,eq=brightness=-0.25\" -pix_fmt yuv420p \"{{}}\"", "brightnesss_low"))
    converters.append((f"{converter} -nostdin -y -v 0 -vsync passthrough -i \"{{}}\" -vf \"pad=width=ceil(iw/2)*2:height=ceil(ih/2)*2,eq=contrast=0.25\" -pix_fmt yuv420p \"{{}}\"", "contrast_high"))
    converters.append((f"{converter} -nostdin -y -v 0 -vsync passthrough -i \"{{}}\" -vf \"pad=width=ceil(iw/2)*2:height=ceil(ih/2)*2,eq=contrast=-0.25\" -pix_fmt yuv420p \"{{}}\"", "contrast_low"))
    converters.append((f"{converter} -nostdin -y -v 0 -vsync passthrough -i \"{{}}\" -vf \"pad=width=ceil(iw/2)*2:height=ceil(ih/2)*2,rotate=10*PI/180\" -pix_fmt yuv420p \"{{}}\"", "rotate"))
    converters.append((f"{converter} -nostdin -y -v 0 -vsync passthrough -i \"{{}}\" -vf \"pad=width=ceil(iw/2)*2:height=ceil(ih/2)*2,crop=0.75*in_w:0.75*in_h\" -pix_fmt yuv420p \"{{}}\"", "crop"))

    return converters

def transform_videos(videos: list, path: str):
    converters = get_converters()

    for video in videos:
        for converter_cmd, convert_type in converters:
            output = os.path.join(path, f"{convert_type}_{os.path.basename(video)}")
            cmd = converter_cmd.format(video, output)

            logger.info(cmd)
            
            subprocess.Popen(cmd, shell=True).wait()

def main():
    logger.info("Running transform videos!")

    if not util.is_frontend_setup():
        logger.error("setup_frontend.py must be run first")
        return

    if len(sys.argv) != 3:
        logger.error("You must provide a valid input path and output directory")
        return

    try:
        input_path = _is_valid_input(sys.argv[1])
    
        _, videos, _ = preprocess.run(input_path)

        if not videos:
            raise Exception("No videos were found at the input path")

        output_path = get_valid_output(sys.argv[2])
    except Exception as e:
        logger.error(str(e))
        return

    transform_videos(videos, output_path)

    logger.info("Finished transform videos!")

if __name__ == "__main__":
    main()