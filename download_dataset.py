import sys
import os
import subprocess

from src import logger

def main():
    if len(sys.argv) != 2:
        logger.error("Requires an output directory")
        return

    output = os.path.abspath(sys.argv[1])

    if not os.path.isdir(output):
        logger.error("Ouput path is not a directory")
        return

    base_cmd_images = f"python -m awscli s3 sync --no-sign-request s3://multimedia-commons/data/images/{{0}} {output}/images/{{0}}"
    base_cmd_videos = f"python -m awscli s3 sync --no-sign-request s3://multimedia-commons/data/videos/mp4/{{0}} {output}/videos/{{0}}"

    logger.info(f"Downloading the dataset")

    # Yes I know these loops are basically identical.
    # Yes they can be improved.
    for i in range(0, 256, 8):
        p_handles = []

        try:
            for j in range (i, i + 8):
                hex_i = hex(j)[2:].rjust(3, '0')
                p_handles.append(subprocess.Popen(base_cmd_images.format(hex_i), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
                p_handles.append(subprocess.Popen(base_cmd_videos.format(hex_i), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
            
            for p_handle in p_handles:
                p_handle.wait()
        except KeyboardInterrupt as e:
            logger.error("Interrupted download. Terminating running download processes")

            for p_handle in p_handles:
                p_handle.terminate()
            
            raise e
    
        logger.info(f"Downloaded {i + 8}/256 of the general dataset")

    for i in range(256, 512, 8):
        p_handles = []
        
        try:
            for j in range (i, i + 8):
                hex_i = hex(j)[2:].rjust(3, '0')
                p_handles.append(subprocess.Popen(base_cmd_videos.format(hex_i), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))

            for p_handle in p_handles:
                p_handle.wait()
        except KeyboardInterrupt as e:
            logger.error("Interrupted download. Terminating running download processes")

            for p_handle in p_handles:
                p_handle.terminate()
            
            raise e

        logger.info(f"Downloaded {(i - 248) }/256 of the additional video dataset")

    logger.info(f"Finished downloading the dataset")

if __name__ == "__main__":
    main() 