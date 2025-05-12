from pathlib import Path
from PIL import Image
import numpy as np

from apps.common.cli.constants.constants import *

#-------------------------------------------------------
# Read the file
def read_file(path: str) -> bytes:
    with open(path, 'rb') as f: 
        return f.read()

# Read image file into a numpy array
def read_image(path: str) -> np.ndarray:
    return np.array(Image.open(path))

# Read the base file
def read_base_file(path: str) -> dict:
    # If the file has a valid image extension
    if Path(path).suffix in IMAGE_EXTS:
        return {
            "file_type": "image",
            "arr": read_image(path)
        }
    # If the file doesn't have a valid extension, raise an exception
    else:
        raise Exception("Invalid base file type")

#-------------------------------------------------------

# Write file in a path
def write_file(file: bytes, path: str) -> None:
    with open(path, 'wb') as f: 
        f.write(file)

# Write image array to a file
def write_image(arr, path):
    Image.fromarray(arr).save(path)
