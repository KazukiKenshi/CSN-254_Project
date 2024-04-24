from django.shortcuts import render
from django.conf import settings
from django.shortcuts import redirect
import speech_recognition as s # type: ignore
import json
from django.http import JsonResponse
from django.http import HttpResponseNotFound
import requests
from django.http import FileResponse
import gtts # type: ignore
import os
from groq import Groq # type: ignore
import re
import pydub
from pydub import AudioSegment
import subprocess
from .models import ChatMessage




def process_speech(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query')
            # Perform any processing here...
              # Function to generate audio URL
            raw_response = llama(query)
            print("Raw Response:", raw_response,"\n")
            anim_data = animDataGenerator(raw_response)
            response = anim_data['response']
            animations = anim_data['anim']

            if query is not None:
                
                audio_files = text_to_speech(response)
                combine_audios(audio_files)
                audio_url = generate_audio_url(query)
                print("Message received:", query,"\n")
                print("Audio URL generated:", audio_url,"\n")
                print("Response generated:", response,"\n")

                chat_message_user = ChatMessage(role='user', content=query)
                chat_message_user.save()
                chat_message_assistant = ChatMessage(role='assistant', content= "".join(response))
                chat_message_assistant.save()

                return JsonResponse({'message': query, 'audio_url': audio_url, 'anim': animations}, status=200)
            else:
                return JsonResponse({'error': 'Query not found in request'}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


def generate_audio_url(query):
    # Generate the audio file path based on the query
    # audio_file_path = os.path.join(settings.MEDIA_ROOT, f'{query}.mp3')
    audio_file_path = os.path.join(settings.MEDIA_ROOT, 'speech.mp3')
    print("media root : " , settings.MEDIA_ROOT)
    print("file path" ,audio_file_path)
    
    # Check if the audio file exists
    if os.path.exists(audio_file_path):
        # If the file exists, generate and return its URL
        # audio_url = os.path.join(settings.MEDIA_URL, f'{query}.mp3')
        audio_url = os.path.join(settings.MEDIA_URL, 'speech.mp3')
        audio_url = settings.MEDIA_URL
        return audio_url
    else:
        # If the file does not exist, return None
        return None



def speech_to_text(request):
    if request.method == 'POST':
        sr = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            try:
                audio = sr.listen(source, timeout=5)  # Adjust timeout as needed
                query = sr.recognize_google(audio, language='en-IN')
                print("Speech recognized:", query)
                response = requests.post('/process-speech/', data={'query': query})
                if response.status_code == 200:
                    return JsonResponse({'message': 'Speech-to-text processing complete.'}, status=200)
                else:
                    return JsonResponse({'error': 'Error processing speech data'}, status=500)
            except sr.WaitTimeoutError:
                # Handle timeout by asking user to speak again
                return JsonResponse({'error': 'Speech timeout. Please try again.'}, status=400)
            except sr.UnknownValueError:
                # Handle unknown speech by asking user to repeat
                return JsonResponse({'error': 'Unknown speech. Please repeat.'}, status=400)
            except sr.RequestError:
                return JsonResponse({'error': 'Speech service unavailable. Please try again later.'}, status=500)
            except Exception as e:
                # Catch unexpected exceptions (e.g., noise interruption) and continue listening
                print("Error:", e)
                return JsonResponse({'error': 'Unexpected error occurred. Please try again.'}, status=400)

    return render(request, 'Speech/stt.html')



def llama(query):
    client = Groq(
        api_key="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",
    )

    chat = [
            {
                "role": "system",
                "content": "You are a girl named Lumina a mental health counsellor. You are compassionate and cute. You include your expression and gesture at appropriate places, expression contained within # and gesture contained within $ like #smile# Hi there!. $wave$ I am Lumina .You only have neutral, happy, sad, smile, surprised, worried expressions. You only have idle, waving, angry, bashful, clap, thumbsUp gestures. Also reset the expression with neutral and gesture with idle whenever necessary."
            }
        ]

    
    
    chat_messages = ChatMessage.objects.all()
    
    for message in chat_messages:
        chat.append({"role" : message.role, "content" : message.content})
        
    chat.append({"role" : "user", "content" : query})
    
    completion = client.chat.completions.create(
    model="llama3-70b-8192",
    messages=chat,
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=False,
    stop=None,
    )
    response = completion.choices[0].message.content;
    print(response)
    return response
    
    
def text_to_speech(sentences):
    audio_files = []
    for idx, text in enumerate(sentences):
        if text:
            # Convert text to string if it's in bytes format
            if isinstance(text, bytes):
                text = text.decode('utf-8')
            
            # Convert text to speech
            tts = gtts.gTTS(text, lang="en")
            
            # Save the speech as an audio file
            audio_file_path = os.path.join(settings.MEDIA_ROOT, 'speech_' + str(idx) + '.mp3')
            tts.save(audio_file_path)
            
            audio_files.append(audio_file_path)
            print("Audio file generated:", audio_file_path,"\n")
    return audio_files
    
    

def combine_audios(audio_files):
    
    ffmpeg_path = os.path.join(settings.BIN_ROOT,'ffmpeg.exe')
    output_path = os.path.join(settings.MEDIA_ROOT,'speech.mp3')
    command = str(ffmpeg_path) + ' -y '
    
    for file in audio_files:
        
        command += ' -i ' + str(file)
    
    command += ' -filter_complex "'
    
    for i in range(0, len(audio_files)):
        command += '[' + str(i) + ':a]'
    
    command += 'concat=n=' + str(len(audio_files)) + ':v=0:a=1" '+str(output_path)
    
    print(command)

    subprocess.run(command, shell=True)
    
    
def serve_audio(request):
    # Extract the filename from the request URL
    # filename = request.path.split('/')[-1]
    filename = "speech.mp3"

    # Determine the path to the audio file
    audio_path = os.path.join(settings.MEDIA_ROOT, filename)
    print("audio path : " , audio_path)
    
    if os.path.exists(audio_path):
        return FileResponse(open(audio_path, 'rb'), content_type='audio/mpeg')
    else:
        return HttpResponseNotFound("Audio file not found")


def animDataGenerator(raw_response):
    IsHash = False
    IsDollar = False
    dat = ""
    animations = []
    sentences = []

    for ch in raw_response:
        if ch == '#':
            if IsHash:
                IsHash = False
                animDat = (dat.strip(), len(sentences))
                animations.append(animDat)
                dat = ""
            else:
                IsHash = True
                if dat.strip() != "":
                    sentences.append(dat.strip())
                dat = ""
        elif ch == '$':
            if IsDollar:
                IsDollar = False
                animDat = (dat.strip(), len(sentences))
                animations.append(animDat)
                dat = ""
            else:
                IsDollar = True
                if dat.strip() != "":
                    sentences.append(dat.strip())
                dat = ""
        else:
            dat += ch

    if dat.strip() != "":
        sentences.append(dat.strip())

    anim_data = {
        'anim': animations,
        'response': sentences
    }

    return anim_data
    