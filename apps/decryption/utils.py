from apps.common.cli.constants.constants import *
import os

def update_cover_image_and_keys(cover_image, key, key2):
    """Updates the cover image and encryption keys with proper error handling"""
    
    if not cover_image:
        return {'status': 'error', 'message': 'No cover image provided'}
        
    if not key or not key2:
        return {'status': 'error', 'message': 'Both encryption keys are required'}

    try:
        print("from utils", cover_image, key, key2)
        # Create directories if they don't exist
        os.makedirs(MOD_IMAGES_PATH, exist_ok=True)
        os.makedirs(ENCRYPTION_KEYS_PATH, exist_ok=True)

        # Save cover image
        cover_image_path = f"{MOD_IMAGES_PATH}/stego_output.png"
        try:
            # Remove existing file if it exists
            if os.path.exists(cover_image_path):
                os.remove(cover_image_path)
                
            with open(cover_image_path, 'wb') as dest_file:
                if hasattr(cover_image, 'read'):
                    # Handle file-like objects (e.g. InMemoryUploadedFile)
                    for chunk in cover_image.chunks():
                        dest_file.write(chunk)
                else:
                    # Handle bytes directly
                    dest_file.write(cover_image)
                    
            # Verify file was written successfully
            if not os.path.exists(cover_image_path):
                return {'status': 'error', 'message': 'Failed to verify cover image was saved'}
                
        except IOError as e:
            return {'status': 'error', 'message': f'Failed to save cover image: {str(e)}'}

        # Update AES key
        try:
            aes_key_path = f"{ENCRYPTION_KEYS_PATH}/aes_key.key"
            with open(aes_key_path, 'wb') as dest_file:
                dest_file.write(key.encode())
            if not os.path.exists(aes_key_path):
                return {'status': 'error', 'message': 'Failed to verify AES key was saved'}
        except IOError as e:
            return {'status': 'error', 'message': f'Failed to update AES key: {str(e)}'}

        # Update quantum key  
        try:
            quantum_key_path = f"{ENCRYPTION_KEYS_PATH}/quantum_key.key"
            with open(quantum_key_path, 'wb') as dest_file:
                dest_file.write(key2.encode())
            if not os.path.exists(quantum_key_path):
                return {'status': 'error', 'message': 'Failed to verify quantum key was saved'}
        except IOError as e:
            return {'status': 'error', 'message': f'Failed to update quantum key: {str(e)}'}

        return {
            'status': 'success',
            'message': 'Cover image and encryption keys updated successfully'
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Unexpected error occurred: {str(e)}'
        }




