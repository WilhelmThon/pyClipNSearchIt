import os
import platform
import json
import itertools

from src import structures

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
_cache = None

def is_backend_setup(client) -> bool:
    return client.indices.exists(index="hashes")

def is_frontend_setup() -> bool:
    if os.path.exists(os.path.join(ROOT_DIR, ".tmp")):
        return True
    return False

def get_config() -> dict:
    global _cache

    if _cache is None:
        config_path = os.path.join(ROOT_DIR, "config.json")
        
        try:
            with open(config_path, 'r') as file:
                _cache = json.load(file)
        except:
            pass

    return _cache

def get_converter(*, ignore_settings: bool = False) -> str:
    system_name = platform.system()

    if system_name == 'Windows':
        converter = os.path.join(ROOT_DIR, "ffmpeg.exe")
    elif system_name == 'Linux':
        converter = "ffmpeg"

    if ignore_settings:
        hwaccel_setting = False
        frame_capture_setting = 1
    else:
        conf = get_config()["ffmpeg"]
        hwaccel_setting = conf["use_hwaccel"]
        frame_capture_setting = conf["capture_every_n_seconds"]

    hwaccel_arg = "-c:v h264_cuvid " if hwaccel_setting else ""
    # Source: https://superuser.com/questions/1486102/fast-way-to-extract-images-from-video-using-ffmpeg
    # This is faster than using the -r argument because it uses a select filter 
    # mod(t,3) -> every 3 seconds
    # ld(2)+1 -> output 1 frame
    filter_arg = f"-vf \"select='if(not(floor(mod(t,{frame_capture_setting})))*lt(ld(1),1),st(1,1)+st(2,n)+st(3,t));if(eq(ld(1),1)*lt(n,ld(2)+1),1,if(trunc(t-ld(3)),st(1,0)))'\" "
    
    return f"{converter} -nostdin -y -v 0 -vsync passthrough {hwaccel_arg}-i \"{{}}\" {filter_arg}-f image2 \"{{}}\""
    

def get_file_type(path: str) -> structures.FileType:
    _, ext = os.path.splitext(path)
    ext = ext.lower()

    if ext in (".png", ".jpg", ".jpeg"):
        return structures.FileType.IMAGE
    elif ext == ".mp4":
        return structures.FileType.VIDEO
    elif ext == ".pregenhashes":
        return structures.FileType.HASHES
    
    return structures.FileType.INVALID

def dict_to_chunks(dct: dict, number: int):
    lst_length = len(dct)
    it = iter(dct)

    chunk_remainder = lst_length % number
    
    if chunk_remainder == 0:
        chunk_size = int(lst_length / number)
        
        for _ in range(0, lst_length, chunk_size):
            yield {key:dct[key] for key in itertools.islice(it, chunk_size)}
    else:
        chunk_size = round(lst_length / number)
        remainder_end = lst_length - chunk_remainder

        for _ in range(0, remainder_end, chunk_size):
            yield {key:dct[key] for key in itertools.islice(it, chunk_size)}
        yield {key:dct[key] for key in it}

def list_to_chunks(lst: list, number: int):
    lst_length = len(lst)
    
    chunk_remainder = lst_length % number
    
    if chunk_remainder == 0:
        chunk_size = int(lst_length / number)
        
        for i in range(0, lst_length, chunk_size):
            yield lst[i:i+chunk_size]
    else:
        chunk_size = round(lst_length / number)
        remainder_end = lst_length - chunk_remainder
        
        for i in range(0, remainder_end, chunk_size):
            yield lst[i:i+chunk_size]
        yield lst[remainder_end:]