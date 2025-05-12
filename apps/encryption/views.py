from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from apps.common.cli.menu import inject_file_func
from .utils import update_folder_files
from django.views.decorators.csrf import csrf_exempt
import json
from apps.common.cli.config import TEST_MODE
import time
from apps.common.cli.constants.constants import *
import logging
from django.http import FileResponse

logger = logging.getLogger(__name__)

@csrf_exempt
def embed_file_func(request):
    try:
        # Check if files were uploaded
        cover_image = request.FILES.get('cover_image')
        files = request.FILES.getlist('files')
        
        if not cover_image:
            return JsonResponse({'error': 'No cover image provided'}, status=400)
        
        if not files:
            return JsonResponse({'error': 'No files provided to embed'}, status=400)
        
        # Update folder files
        result = update_folder_files(cover_image, files)
        
        if result.get('status') == 'error':
            return JsonResponse({'error': result.get('message')}, status=500)
        
        # Inject the file
        try:
            t1 = time.time()
            quantum_encrypted_file, out_path, correlation, aes_path = inject_file_func()
            time_taken = (round(time.time() - t1, 4))
            
            # Debug logging
            logger.info(f"Injection results - correlation: {correlation}, time_taken: {time_taken}")
            logger.info(f"quantum_encrypted_file: {quantum_encrypted_file}")
            logger.info(f"out_path: {out_path}")
            
            # Check if the response is an error message (single string)
            if isinstance(time_taken, str) and time_taken.startswith('\n'):
                return JsonResponse({'error': time_taken}, status=500)
                
            # read keys
            # Read AES key
            try:
                with open(f'{ENCRYPTION_KEYS_PATH}/aes_key.key', 'rb') as f:
                    aes_key = f.read()
            except FileNotFoundError:
                return JsonResponse({'error': 'AES key file not found'}, status=500)
                
            # Read quantum key
            try:
                with open(f'{ENCRYPTION_KEYS_PATH}/quantum_key.key', 'rb') as f:
                    quantum_key = f.read()
            except FileNotFoundError:
                return JsonResponse({'error': 'Quantum key file not found'}, status=500)

            response_data = {
                'status': 'success',
                'time_taken': time_taken,
                'quantum_encrypted_file': str(quantum_encrypted_file) if quantum_encrypted_file else None,
                'out_path': str(out_path) if out_path else None,
                'aes_path': aes_path,
                'aes_key': str(aes_key),
                'quantum_key': str(quantum_key),
                'correlation': correlation
            }
            
            # Debug logging of final response
            logger.info(f"Final response data: {json.dumps(response_data)}")
            
            # Return success response
            return JsonResponse(response_data)
        except ValueError as e:
            logger.error(f"Injection error: {str(e)}")
            return JsonResponse({'error': f'Injection error: {str(e)}'}, status=500)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        # Return error response
        return JsonResponse({'error': str(e)}, status=500)
    

def download_img(request):
    file = f"{MOD_IMAGES_PATH}/stego_output.png"
    fileOpened = open(file, 'rb')
    
    response = FileResponse(fileOpened, content_type='image/png')
    response['Content-Disposition'] = 'attachment; filename="stego_output.png"'
    
    return response