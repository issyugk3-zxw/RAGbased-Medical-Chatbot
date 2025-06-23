from django.urls import path
from . import views

urlpatterns = [
    path('audio/transcribe', views.transcribe_audio, name='transcribe_audio'),
    path('download-pdf', views.download_pdf, name='download_pdf'),
] 