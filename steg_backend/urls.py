from django.urls import path
from apps.encryption.views import embed_file_func, download_img
from apps.decryption.views import decrypt_file_func, download_zip

urlpatterns = [
    path("embed/", embed_file_func, name="embed"),
    path("decrypt/", decrypt_file_func, name="decrypt"),
    path('download_zip/',download_zip,name="download_zip"),
    path('download_img/',download_img,name='download_img')
]
