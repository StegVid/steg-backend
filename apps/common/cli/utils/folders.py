import os
from pathlib import Path

from constants.constants import *
from utils.ctxt import *

# Create folders if they don't exist
def create_folders(*args: str) -> None:
    for folder in args:
        os.makedirs(folder, exist_ok=True)  # Ensure folder exists

# Convert image file extensions (e.g., .jpg → .png)
def folder_convert(folder: str, extension: str, valid_exts: list) -> None:
    for file in os.listdir(folder):
        ext = Path(file).suffix
        stem = Path(file).stem
        if ext in valid_exts and ext != extension:
            os.rename(f"{folder}/{file}", f"{folder}/{stem}{extension}")
            print(ctxt(f"Converted {file} to {stem}{extension}", Fore.GREEN))
