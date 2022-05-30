import os
import subprocess
import imagehash
import multiprocessing as mp

from collections import defaultdict
from PIL import Image
from src import util

def _p_hash_img(files: list) -> dict:
    hash_sets = {}

    for file in files:
        try:
            image = Image.open(file)
            name = os.path.basename(file)
            hash_sets[name] = str(imagehash.phash(image, 8))
        except:
            pass

    return hash_sets

def _p_hash_vid(files: list) -> dict:
    hash_sets = defaultdict(dict)
    _setting_frame_capture = util.get_config()["ffmpeg"]["capture_every_n_seconds"]

    for file in files:
        try:
            image = Image.open(file)
            name, frame = os.path.splitext(os.path.basename(file))
            # By using the hash as the key, we ensure that no duplicate frames are ever saved
            # effectively performing a uniqueness filter whilst processing!
            #
            # The set value represents the frame timestamp ->  (ffmpeg output digit - 1) * seconds skipped (see util.get_converter())
            hash_sets[name][str(imagehash.phash(image, 8))] = (int(frame[1:]) - 1) * _setting_frame_capture
        except:
            pass

    return hash_sets

def _hash_images(pool: mp.Pool, images: list, hash_sets: dict):
    for result in pool.imap_unordered(_p_hash_img, util.list_to_chunks(images, pool._processes)):
        hash_sets |= result

def _hash_videos(pool: mp.Pool, videos: list, hash_sets: dict):
    tmp_dir = os.path.join(util.ROOT_DIR, ".tmp")
    base_cmd = util.get_converter()
    videos_len = len(videos)

    for i in range(0, videos_len, 20):
        videos_left = videos_len - i
        remaining = videos_left if videos_left < 20 else 20

        for j in range(i, i + remaining):
            output = os.path.join(tmp_dir, f"{os.path.basename(videos[j])}.%d")
            cmd = base_cmd.format(videos[j], output)
            subprocess.Popen(cmd, shell=True).wait()

        images = []

        with os.scandir(tmp_dir) as it:
            for entry in it:
                images.append(entry.path)

        for result in pool.imap_unordered(_p_hash_vid, util.list_to_chunks(images, pool._processes)):
            for key in result:
                existing_dict = hash_sets.get(key, None)
                
                if existing_dict:
                    existing_dict |= result[key]
                else:
                    hash_sets[key] = result[key]

        # This is to ensure we do not blow up the disk space
        for image in images:
            os.remove(image)

def run(images: list, videos: list) -> list:    
    hash_sets = {}

    if images or videos:
        pool = mp.Pool(processes=mp.cpu_count())

        if images:
            _hash_images(pool, images, hash_sets)

        if videos:
            _hash_videos(pool, videos, hash_sets)

        pool.close()

    return hash_sets