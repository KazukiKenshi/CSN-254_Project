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
from groq import Groq
import re

#
#
#-------------- time the animations and expressions by slicing the response into sentences, adding the duration of audio file as the delay
#               and playing files in sequence ----------------------------------
#

def process_speech(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query')
            # Perform any processing here...
            audio_url = generate_audio_url(query)  # Function to generate audio URL
            rawResponse = llama(query)
            print("Raw Response : ", rawResponse, " \n\n")
            anim_data = animDataGenerator(rawResponse)
            
            response = anim_data['response']
            
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        if query is not None:
            print("Message received:")
            print(query)
            print("Audio URL generated:")
            print(audio_url)
            # Decode the response if it's in bytes format
            if isinstance(response, bytes):
                response = response.decode('utf-8')
            
            print("Response generated:")
            print(response)
            text_to_speech(response)
            expression = anim_data['expression'][0]
            anim = anim_data['anim'][0]
                
            return JsonResponse({'message': query, 'audio_url': audio_url, 'expression' : expression, 'anim' : anim}, status=200)
        else:
            return JsonResponse({'error': 'Query not found in request'}, status=400)

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
    
    
def text_to_speech(text):
    if text:
        # Convert text to string if it's in bytes format
        if isinstance(text, bytes):
            text = text.decode('utf-8')
        
        # Convert text to speech
        tts = gtts.gTTS(text, lang="en")
        
        # Save the speech as an audio file
        audio_file_path = os.path.join(settings.MEDIA_ROOT, 'speech.mp3')
        tts.save(audio_file_path)
        
        # Render the template with the audio file path
        print("audio file generated\n")
    else:
        print("no text provided\n")

        

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


def animDataGenerator(rawResponse):
    
    
    pattern1 = r'#(.*?)#'
    pattern2 = r'\$(.*?)\$'

    expressions = re.findall(pattern1, rawResponse)
    animations = re.findall(pattern2, rawResponse)
    response = re.sub(pattern1, '', rawResponse)
    response = re.sub(pattern2, '', response)
    
    anim_data = {
        'expression': expressions,
        'anim': animations,
        'response' : response
    }
    
    return anim_data
    
    
    
    




# def process_speech(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             query = data.get('query')
#             # Perform any processing here...
#             audio_url = generate_audio_url(query)  # Function to generate audio URL
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON data'}, status=400)

#         if query is not None:
#             print("Message received:")
#             print(query)
#             print("Audio URL generated:")
#             print(audio_url)
#             return JsonResponse({'message': query, 'audio_url': audio_url}, status=200)
#         else:
#             return JsonResponse({'error': 'Query not found in request'}, status=400)

#     return JsonResponse({'error': 'Method not allowed'}, status=405)