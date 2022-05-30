from enum import Enum

class MenuOptions(Enum):
    STATISTICS = 0
    INDEX = 1
    SEARCH = 2

class FileType(Enum):
    INVALID = 0
    IMAGE = 1
    VIDEO = 2
    HASHES = 3