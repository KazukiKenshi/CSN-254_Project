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

def process_speech(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query')
            # Perform any processing here...
            audio_url = generate_audio_url(query)  # Function to generate audio URL
            response = llama(query)
            
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
            
            try:
                response_json = json.loads(response)
                content = response_json.get('message', {}).get('content')
                if content:
                    print("Response generated:")
                    print(content)
                    text_to_speech(content)
                else:
                    print("Invalid response format:", response_json)
            except json.JSONDecodeError:
                print("Invalid JSON format for response:", response)
            
            return JsonResponse({'message': query, 'audio_url': audio_url}, status=200)
        else:
            return JsonResponse({'error': 'Query not found in request'}, status=400)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

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
    

    # Define the API endpoint URL
    url = "http://localhost:11434/api/chat"

    # Define the request payload
    payload = {
    "model": "llama3",
    "stream" : False,
    "messages": [
        {
        "role": "user",
        "content": query
        }
    ]
    }


    # Make a POST request with payload
    response = requests.post(url, json=payload)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Print the raw response content
        # print("Raw Response:", response.content)
        return response.content
    else:
        # Print an error message if the request failed
        print("Error:", response.status_code)
        return response.status_code
    
    
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
    