import sys
import logging
import time

from time import time_ns

class _Record(logging.LogRecord):
    def __init__(self, *args, **kwargs):
        self.created_timestamp = time_ns()
        super().__init__(*args, **kwargs)

class _Formatter(logging.Formatter):
    def __init__(self, fmt):
        super().__init__(fmt)
        self.color_formats = {
            logging.DEBUG: "\x1b[38;21m{}\x1b[0m",
            logging.INFO: "\x1b[38;21m{}\x1b[0m",
            logging.WARNING: "\x1b[38;5;226m{}\x1b[0m",
            logging.ERROR: "\x1b[38;5;196m{}\x1b[0m",
            logging.CRITICAL: "\x1b[31;1m{}\x1b[0m"
        }

    def format(self, record):
        fmt = super().format(record)
        return self.color_formats[record.levelno].format(fmt)

    def formatTime(self, record, datefmt=None):
        if datefmt is not None:
            return super().formatTime(record, datefmt)
        
        timestamp = time.strftime(self.default_time_format, self.converter(record.created_timestamp / 1e9))
        
        return "%s,%09d" % (timestamp, record.created_timestamp - (record.created_timestamp // 10**9) * 10**9)

def _init_logger():
    logging.setLogRecordFactory(_Record)
    logger = logging.getLogger("pySearchClipIt")
    logger.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(_Formatter("%(asctime)s [%(levelname).4s] %(message)s"))

    logger.addHandler(ch)

    return logger

sys.modules[__name__] = _init_logger()