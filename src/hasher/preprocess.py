import os

from src import util
from src import structures

def _collect(path: str) -> tuple:
    images = []
    videos = []
    pregen = []

    for root, _, files in os.walk(path):
        for file in files:
            file_type = util.get_file_type(file)
            path = os.path.join(root, file)

            if file_type == structures.FileType.IMAGE:
                images.append(path)
            elif file_type == structures.FileType.VIDEO:
                videos.append(path)
            elif file_type == structures.FileType.HASHES:
                pregen.append(path)

    return images, videos, pregen

def run(path: str) -> tuple:
    if os.path.isfile(path):
        file_type = util.get_file_type(path)

        if file_type == structures.FileType.IMAGE:
            return [path], None, None
        elif file_type == structures.FileType.VIDEO:
            return None, [path], None
        elif file_type == structures.FileType.HASHES:
            return None, None, [path]
    else:
        return _collect(path)