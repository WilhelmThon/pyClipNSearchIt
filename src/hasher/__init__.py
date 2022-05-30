__all__ = ('preprocess', 'process')

import argparse
import json

from src import logger
from . import preprocess
from . import process

def _read_from_file(path: str, hash_sets: dict):
    with open(path) as file:
        hash_sets |= json.load(file)

def _write_to_file(path: str, hash_sets: dict):
    with open(path, 'w') as file:
        json.dump(hash_sets, file, indent=4)

def run(args: argparse.Namespace) -> dict:
    logger.info("Preprocessing files, please wait...")
    images, videos, pregen = preprocess.run(args.input)
    logger.info("Finished preprocessing files!")
    logger.info("Generating hashes, please wait...")
    hash_sets = process.run(images, videos)
    logger.info("Finised generating hashes!")

    # Decrement counter for gc to kick in before we start
    # reading potential pregens
    images = None
    videos = None

    if pregen:
        logger.info("Reading pre-generated hashes, please wait...")
        for path in pregen:
            _read_from_file(path, hash_sets)
        logger.info("Finished reading pre-generated hashes!")

    if not hash_sets:
        raise Exception("No hashes could be calculated or read from the input")

    if args.output:
        logger.info("Writing hashes to file, please wait...")
        _write_to_file(args.output, hash_sets)
        logger.info("Finished writing hashes!")

    return hash_sets