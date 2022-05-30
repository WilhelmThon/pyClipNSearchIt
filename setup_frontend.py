import sys
import os
import platform
import subprocess
import json

from src import logger
from src import util

FILE_DIR = os.path.dirname(__file__)
CONFIG = {
    "elasticsearch": {
        "hosts": [
            "https://localhost:9200"
        ],
        "http_auth": [
            "user",
            "password"
        ],
        "verify_certs": False,
        "ssl_show_warn": False
    },
    "elasticsearch_index": {
        "number_of_shards": 9,
        "number_of_replicas": 1
    },
    "ffmpeg": {
        "use_hwaccel": False,
        "capture_every_n_seconds": 1
    },
    "search": {
        "max_size_response": 15,
        "r": 5
    }
}

def install_requirements_pip():
    logger.info("...Attempting to install pip requirements")
    # These are included to ensure we don't encounter any weird errors when installing the requirements
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", 'pip'])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", 'setuptools'])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", 'distlib'])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", 'requests'])
    # Install requirements
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", os.path.join(FILE_DIR, "requirements.txt")])
    logger.info("...Success, installed pip requirements")

def install_requirements_windows():
    import ssl
    from urllib.request import urlopen, Request
    from urllib.error import URLError
    from http.client import IncompleteRead
    from io import BytesIO
    from zipfile import ZipFile

    # Download and install ffmpeg
    try:
        logger.info("...Attempting to download ffmpeg")
        http_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

        context = ssl._create_unverified_context()

        with urlopen(Request(
            url="https://www.gyan.dev/ffmpeg/builds/git-version",
            headers=http_header),
            context=context
        ) as response:
            content = response.read()
            encoding = response.headers.get_content_charset('utf-8')
            ffmpeg_version = content.decode(encoding)

        logger.info(f"...Latest ffmpeg git version is {ffmpeg_version}")

        with urlopen(Request(
            url=f"https://github.com/GyanD/codexffmpeg/releases/download/{ffmpeg_version}/ffmpeg-{ffmpeg_version}-essentials_build.zip",
            headers=http_header),
            context=context
        ) as response:
            url_file = BytesIO(response.read())
        logger.info("...Success, downloaded ffmpeg")

    except (URLError, IncompleteRead) as e:
        logger.error(f"Failed to download ffmpeg '{e}'")
        quit()

    with ZipFile(url_file, mode = 'r') as zipObj:
        logger.info("...Extracting ffmpeg from archive")
        for zip_info in zipObj.infolist():
            if zip_info.filename[-1] == '/': continue

            basename = os.path.basename(zip_info.filename)

            if not basename == 'ffmpeg.exe': continue

            zip_info.filename = basename
            zipObj.extract(zip_info, path=FILE_DIR)
            break
        logger.info("...Success, extracted ffmpeg.exe from archive")
    
def install_requirements_linux():
    logger.info("...Attempting to download dependencies")
    subprocess.check_call(['sudo', 'add-apt-repository', 'ppa:savoury1/ffmpeg4'], stdout=sys.stdout, stderr=sys.stderr)
    subprocess.check_call(['sudo', 'apt', 'install'] + ['ffmpeg', 'libjpeg8-dev', 'zlib1g-dev', 'python3.9-distutils'] + ['-y'], stdout=sys.stdout, stderr=sys.stderr)
    logger.info("...Success, dependencies downloaded")

def main():
    logger.info("Running frontend setup!")

    if util.is_frontend_setup():
        logger.error("setup_frontend.py has already been run!")
        return

    system_name = platform.system()

    # System specific install requirements
    if system_name == 'Windows':
        install_requirements_windows()
    elif system_name == 'Linux':
        install_requirements_linux()
    else:
        logger.error("You are not on a supported system")
        return

    install_requirements_pip()

    # Create temp data folder
    tmp_dir = os.path.join(util.ROOT_DIR, ".tmp")
    os.mkdir(tmp_dir)
    
    if system_name == 'Windows':
        os.system(f"attrib +h {tmp_dir}")

    # Create config
    config_file = os.path.join(util.ROOT_DIR, "config.json")
    with open(config_file, 'w+') as file:
        json.dump(CONFIG, file, indent=4)

    logger.info("Created config.json. Remember to edit the default configuration!")
    logger.info("Finished running frontend setup!")

if __name__ == "__main__":
    main()