
import json
import logging
from pathlib import Path
import subprocess
import tempfile

logger = logging.getLogger()

class ImageNotFound(Exception):
    pass

def extract_sbom_syft(docker_image_id:str, logger=logger):
    """
    returns syft format as dict
    throws ImageNotFound when image tag not found in registry
    throws on any other error
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        target_file =  Path(tmpdirname,'output.json')

        proc = subprocess.Popen(["syft",
            f"registry:docker.io/{docker_image_id}",
            "-v",
            "-o",
            f"json={target_file.as_posix()}"], 
            bufsize=1, 
            universal_newlines=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT)
        for line in proc.stdout:
            logger.info(line.strip())
            if 'could not fetch image' in line:
                raise ImageNotFound()
        proc.wait()
        if proc.returncode != 0:
            raise subprocess.CalledProcessError()
        with open(target_file) as fin: 
            return json.load(fin)
