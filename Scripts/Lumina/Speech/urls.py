from django.urls import path
from .views import speech_to_text
from .views import llama
from .views import process_speech
from .views import serve_audio

urlpatterns = [
    path('stt/', speech_to_text, name='stt'),
    # path('llama/<str:query>/',llama, name='llama'),
    path('process-speech/', process_speech, name='process_speech'),
    path('media/', serve_audio, name='serve_audio'),
]
