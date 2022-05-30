import os
import argparse

from src import util
from src import structures

def _is_valid_input(path: str) -> str:
    abs_path = os.path.abspath(path)

    if os.path.isdir(abs_path):
        return abs_path
    elif os.path.isfile(abs_path): 
        if util.get_file_type(path) != structures.FileType.INVALID:
            return abs_path
            
        raise argparse.ArgumentTypeError("The input file is not a valid file type")
    else:
        raise argparse.ArgumentTypeError("The input path is not an existing file nor directory")

def _is_valid_output(path: str) -> str:
    path = os.path.splitext(path)[0]

    if path[0] == '.':
        raise argparse.ArgumentTypeError("The output path cannot be an extension type")

    abs_path = os.path.abspath(path)

    if os.path.isdir(abs_path):
        raise argparse.ArgumentTypeError("The output path cannot be a directory")
    if os.path.isfile(abs_path):
        raise argparse.ArgumentTypeError("The output path cannot be an existing file") 

    return f"{abs_path}.pregenhashes"

def is_empty(args: argparse.Namespace) -> bool:
    return not any(vars(args).values())

def parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="pyClipNSearchIt")

    parser.add_argument("-i", "--input", dest="input", help="Directory/File path", type=_is_valid_input)
    parser.add_argument("-o", "--output", dest="output", help="Destination file path", type=_is_valid_output)

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--add", dest="option", help="Index images/videos", action="store_const", const=structures.MenuOptions.INDEX)
    group.add_argument("-s", "--search", dest="option", help="Search for images/videos", action="store_const", const=structures.MenuOptions.SEARCH)

    args = parser.parse_args()

    if is_empty(args):
        args.option = structures.MenuOptions.STATISTICS
    else:
        if args.input is None:
            parser.error("An input must be supplied")

        if not (args.output or args.option):
            parser.error("An input must be followed by other options")

    return args