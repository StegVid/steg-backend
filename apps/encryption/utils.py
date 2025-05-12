from apps.common.cli.constants.constants import *
from apps.common.cli.config import TEST_MODE
import os
import shutil

def update_folder_files(cover_image, files):
    """
    This function handles file management operations:
    1. Creates/updates a cover image
    2. Clears existing files in a target folder
    3. Saves new files to the target folder
    
    Args:
        cover_image: File object or bytes containing the cover image
        files: List of file objects to be saved
        
    Returns:
        dict: Status and details of the operation
    """
    try:
        # First, create all required directories
        for path in [BASE_PATH, BASE_IMAGES_PATH, BASE_AUDIOS_PATH,
                    INPUT_PATH, MOD_PATH, MOD_IMAGES_PATH, 
                    MOD_AUDIOS_PATH, OUTPUT_PATH, ENCRYPTION_KEYS_PATH]:
            os.makedirs(path, exist_ok=True)

        # Create the full path to the target folder
        folder_path = f"{INPUT_PATH}/test_folder"        
        cover_image_path = f"{BASE_IMAGES_PATH}/cover_image.png"
        # Ensure the folder exists
        os.makedirs(folder_path, exist_ok=True)
        
        # Update the cover image
        with open(cover_image_path, 'wb') as dest_file:
            if hasattr(cover_image, 'read'):
                for chunk in cover_image.chunks():
                    dest_file.write(chunk)
            else:
                dest_file.write(cover_image)
        
        # Track processed files
        processed_files = []
        
        # Clear existing files in the target folder
        for existing_file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, existing_file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Process each file and save it to the target folder - handle files as a list
        for file_obj in files:
            # Get the file name
            file_name = file_obj.name
            
            # Get the destination path
            dest_path = os.path.join(folder_path, file_name)
            
            # Save the file
            with open(dest_path, 'wb') as dest_file:
                # Read in chunks to handle large files
                for chunk in file_obj.chunks():
                    dest_file.write(chunk)
            
            processed_files.append(file_name)
        
        print(f'Successfully updated {len(processed_files)} files in test_folder')
        return {
            'status': 'success',
            'message': f'Successfully updated {len(processed_files)} files in test_folder',
            'updated_files': processed_files
        }
        
    except Exception as e:
        return {
            'status': 'error', 
            'message': f'Error updating files: {str(e)}'
        }