import sys
import os
import json

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from src import logger
from src import util
from src.structures import FileType

def main():
    logger.info("Running count hashes!")

    if not util.is_frontend_setup():
        logger.error("setup_frontend.py must be run first")
        return

    if len(sys.argv) != 2:
        logger.error("You must provide a .pregenhashes or .pregenhashes.notnormalized.txt input file")
        return

    path = os.path.abspath(sys.argv[1])

    if (not os.path.isfile(path)) or (util.get_file_type(path) != FileType.HASHES and not path.lower().endswith(".pregenhashes.notnormalized.txt")):
        logger.error("The provided path is either not valid or the correct file type (.pregenhashes, .pregenhashes.notnormalized.txt)")
        return

    with open(path) as file:
        hash_sets = json.load(file)

    number_of_hashes = 0

    for origin in hash_sets:
        data = hash_sets[origin]

        if type(data) is str:
            number_of_hashes += 1
        else:
            number_of_hashes += len(data)

    logger.info(f"The number of hashes in {os.path.basename(path)} is {number_of_hashes}")
    logger.info("Finished running count hashes!")

if __name__ == "__main__":
    main()