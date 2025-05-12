from pathlib import Path
import time
import shutil
import zipfile
import os
import numpy as np
from scipy.stats import pearsonr
import cv2

from rustworkx import InvalidNode
from config import *
from .constants.constants import *
from apps.common.cli.classes.Options import Options
from apps.common.cli.utils.cryptography import (
    get_fernet, encrypt_data, decrypt_data,
    encrypt_with_qkd, decrypt_with_qkd
)
from apps.common.cli.utils.ctxt import *
from apps.common.cli.utils.injection import inject_file, extract_file
from apps.common.cli.utils.input import get_path, get_bool
from apps.common.cli.utils.read_write import *

# Toggle Quantum Cryptography (Set to True to Enable)
USE_QUANTUM_CRYPTO = True


def get_out_path(base_path: str, file_type: str) -> str:
    base_stem = Path(base_path).stem
    if file_type == "image":
        out_path = f"{MOD_IMAGES_PATH}/stego_output.png"
    elif file_type == "audio":
        out_path = f"{MOD_AUDIOS_PATH}/{MOD_PREFIX}{base_stem}{MOD_SUFIX}.wav"
    return out_path


def menu() -> None:
    option = Options(["EXIT", "Inject file", "Extract file"]).get_choice()

    if option == 0:
        exit()
    elif option == 1:
        inject_file_func()
    elif option == 2:
        extract_file_func()


def inject_file_func() -> None:
    # Ensure the folder to embed exists
    folder_to_embed = f"{INPUT_PATH}/test_folder"
    if not os.path.exists(folder_to_embed):
        print(f"Error: The folder '{folder_to_embed}' does not exist. Please create it before running the script.")
        return

    # Compress the folder into a ZIP file
    zip_path = f"{INPUT_PATH}/zip_folder.zip"
    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', folder_to_embed)

    file_path = zip_path
    base_path = f"{BASE_IMAGES_PATH}/cover_image.png"

    # Read the file (in bytes)
    file = read_file(file_path)

    # Read the base file and store it in an array
    base_file = read_base_file(base_path)
    arr = base_file["arr"]
    file_type = base_file["file_type"]

    # Get filename (in bytes)
    filename = Path(file_path).name.encode()

    # Encrypt the ZIP file using AES-128
    encrypted_file, fernet = encrypt_data(file)
    file = encrypted_file
    
    # Save the AES-128 encrypted file
    aes_encrypted_path = f"{OUTPUT_PATH}/aes_encrypted_file.png"
    with open(aes_encrypted_path, 'wb') as f:
        f.write(encrypted_file)
    print(ctxt(f"\nAES-128 encrypted file saved in {ctxt(aes_encrypted_path, Fore.YELLOW)}", Fore.GREEN))
    
    # Get the output path
    out_path = get_out_path(base_path, file_type)

    # Save the original base file for correlation comparison
    if file_type == "image":
        original_image = np.array(base_file["arr"])  # The original image array

    try:
        # Inject the file into the array
        new_arr = inject_file(arr, file, filename, True)

        # Write the new array to out_path
        if file_type == "image":
            write_image(new_arr, out_path)

        print(ctxt(f"\nModified {file_type} saved in {ctxt(out_path, Fore.YELLOW)}", Fore.GREEN))

    except Exception as e:
        print(f"\n{ctxt('Error: ', Fore.RED)}{e}")
        return

    # Compute the correlation coefficient between the original and modified image (if it's an image)
    if file_type == "image":
        modified_image = np.array(new_arr)  # The modified image array
        correlation, _ = pearsonr(original_image.flatten(), modified_image.flatten())
        print(f"Correlation coefficient between original and modified image: {correlation:.4f}")

    # Quantum Encrypt `stego_output.png`
    if USE_QUANTUM_CRYPTO:
        quantum_path=encrypt_with_qkd(out_path)

    return(quantum_path,out_path,correlation,aes_encrypted_path)


def extract_file_func() -> None:
    if True:
        mod_file_path = f"{MOD_IMAGES_PATH}/stego_output.png"
    else:
        mod_file_path = get_path([MOD_IMAGES_PATH, MOD_AUDIOS_PATH], "Filename of the modified file: ", [IMAGE_EXTS, AUDIO_EXTS])

    # If Quantum Encryption is enabled, decrypt `stego_output.png`
    if USE_QUANTUM_CRYPTO:
        mod_file_path = decrypt_with_qkd(mod_file_path)

    t1 = time.time()

    # Read the modified array
    if Path(mod_file_path).suffix in IMAGE_EXTS:
        mod_arr = read_image(mod_file_path)

    # Extract the file and filename from the array
    output = extract_file(mod_arr)
    file, filename = output["file"], output['filename']

    # Decrypt the file if it was encrypted using AES-128
    try:
        fernet = get_fernet(1)
        file = decrypt_data(file, fernet)
    except InvalidNode:
        print("\nError: Failed to decrypt file. Ensure the correct key is used.")

    # Decode the filename
    filename = filename.decode("utf-8")

    # Save extracted ZIP file
    out_path = f"{OUTPUT_PATH}/{filename}"
    write_file(file, out_path)
    print(ctxt(f"\nOutput file saved in {ctxt(out_path, Fore.YELLOW)}", Fore.GREEN))

    # Ensure extracted file is a valid ZIP before unzipping
    extract_folder = f"{OUTPUT_PATH}/{Path(filename).stem}"
    try:
        with zipfile.ZipFile(out_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)
        print(f"\nExtracted folder saved in {extract_folder}")
    except zipfile.BadZipFile:
        print("\nError: Extracted file is not a valid zip archive. Check embedding/extraction process.")

    print(f"\nDone in {ctxt(round(time.time() - t1, 4), Fore.GREEN)} seconds")
    return(out_path)
