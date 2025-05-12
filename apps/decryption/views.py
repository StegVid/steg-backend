from django.shortcuts import render
from django.http import FileResponse, HttpResponse
from apps.common.cli.menu import extract_file_func
from django.views.decorators.csrf import csrf_exempt
from apps.decryption.utils import update_cover_image_and_keys
from django.http import JsonResponse
import time
from apps.common.cli.constants.constants import *
from django.http import FileResponse
# Create your views here.

@csrf_exempt
def decrypt_file_func(request):
    cover_image = request.FILES.get('cover_image')
    key = request.POST.get('key')
    key2 = request.POST.get('key2')
    # update cover_image and keys
    result = update_cover_image_and_keys(cover_image, key, key2)
    if result.get('status') == 'error':
        return JsonResponse({'error': result.get('message')}, status=500)
    else:
        try:
            # extract the file
            
            start_time = time.time()
            zip_path = extract_file_func()
            time_taken = round(time.time() - start_time, 4)
            
            return JsonResponse({'message': 'Cover image and keys updated successfully', 'zip_path': zip_path, 'time_taken': time_taken})
        except Exception as e:
            return JsonResponse({'error': f'Decryption failed: {str(e) or "Invalid keys or encrypted data"}'}, status=500)

def download_zip(request):
    file = f"{OUTPUT_PATH}/zip_folder.zip"
    fileOpened = open(file, 'rb')
    
    response = FileResponse(fileOpened, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="zip_folder.zip"'
    
    return response