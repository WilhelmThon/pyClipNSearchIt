import sys
import os
import subprocess
import imagehash

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from collections import defaultdict
from PIL import Image
from distutils.util import strtobool
from src import logger
from src import util
from src.arguments import _is_valid_input, _is_valid_output
from src.hasher import preprocess, _write_to_file

def hash_videos(videos: list):
    if not videos:
        return None

    tmp_dir = os.path.join(util.ROOT_DIR, ".tmp")
    base_cmd = util.get_converter(ignore_settings=True)
    videos_len = len(videos)
    hash_sets = defaultdict(list)

    for i in range(0, videos_len, 20):
        videos_left = videos_len - i
        remaining = videos_left if videos_left < 20 else 20

        for j in range(i, i + remaining):
            output = os.path.join(tmp_dir, f"{os.path.basename(videos[j])}.%d")
            cmd = base_cmd.format(videos[j], output)

            logger.info(cmd)

            subprocess.Popen(cmd, shell=True).wait()

        files = []

        with os.scandir(tmp_dir) as it:
            for entry in it:
                files.append(entry.path)

        for file in files:
            try:
                image = Image.open(file)
                name, frame = os.path.splitext(os.path.basename(file))
                hash_sets[name].append((str(imagehash.phash(image, 8)), int(frame[1:]) - 1))
            except:
                pass

            hash_sets[name].sort(key=lambda x: x[1])

            os.remove(file)

    return hash_sets

def extract_clips(hash_sets: dict, length, offset):
    to_remove = []
    
    for origin in hash_sets:
        data = hash_sets[origin]
        video_length = len(data)

        if video_length < (offset + length):
            logger.info(f"The chosen offset '{offset}' and length '{length}' = {offset+length}, exceeds  the video length of {origin}, '{video_length}'. Skipping the clip")
            to_remove.append(origin)
            continue
        
        hash_sets[origin] = data[offset:offset+length]

    for origin in to_remove:
        del hash_sets[origin]

def normalize_output(hash_sets: dict):
    frame_capture_setting = util.get_config()["ffmpeg"]["capture_every_n_seconds"]

    for origin in hash_sets:
        data = hash_sets[origin]
        tmp_data = {}
        
        for i in range(0, len(data), frame_capture_setting):
            frame, timestamp = data[i]
            tmp_data[frame] = timestamp

        hash_sets[origin] = tmp_data

def main():
    logger.info("Running extract clips!")

    if not util.is_frontend_setup():
        logger.error("setup_frontend.py must be run first")
        return

    num_args = len(sys.argv)

    if num_args < 4 or num_args > 6:
        logger.error("You must provide a valid input path, output path, clip length (int), and optionally an offset (int, default 0) and normalize option (bool, default true)")
        return

    try:
        input_path = _is_valid_input(sys.argv[1])
        output_path = _is_valid_output(sys.argv[2])
        length = int(sys.argv[3])
        offset = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        normalize = strtobool(sys.argv[5].lower()) if len(sys.argv) > 5 else True

        if length <= 0:
            raise Exception("The length must be above 0")

        _, videos, _ = preprocess.run(input_path)
        hash_sets = hash_videos(videos)

        if not hash_sets:
            raise Exception("No hashes could be calculated or read from the input")
    except Exception as e:
        logger.error(str(e))
        return

    # Extract the clips for each video
    extract_clips(hash_sets, length, offset)
    
    if normalize:
        # Normalize the output so the .pregenhashes can be read
        normalize_output(hash_sets)
    else:
        output_path += ".notnormalized.txt"


    _write_to_file(output_path, hash_sets)

    logger.info("Finished running extract clips!")

if __name__ == "__main__":
    main()