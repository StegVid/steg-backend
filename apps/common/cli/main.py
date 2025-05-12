from constants.constants import *
from utils.folders import create_folders, folder_convert
from menu import menu

create_folders(*PATHS)
folder_convert(BASE_IMAGES_PATH, ".png", IMAGE_EXTS)

menu()