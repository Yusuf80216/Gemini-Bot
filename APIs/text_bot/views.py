from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.sessions.backends.db import SessionStore
from rest_framework.decorators import api_view
import google.generativeai as genai
from rest_framework.response import Response
from decouple import config

API_KEY = config("GEMINI_API_KEY")

# Model Initialization
genai.configure(api_key=API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')

hist_dict = {}
dialogue_dict = {}

@api_view(['POST'])
def generate_text(request):
    if request.method == 'POST':
        try:
            session_id = request.data.get('session_id')
            system_prompt = request.data.get('system_prompt', '')
            prompt = request.data.get('prompt')

            if session_id not in hist_dict:
                hist_dict[session_id] = []
            
            chat = gemini_model.start_chat(history=hist_dict[session_id])
            response = chat.send_message([system_prompt,
                                          prompt],
                                          stream=True)
            response.resolve()

            hist_dict[session_id] = chat.history
            
            return Response({"generated_text": response.text})
        except Exception as e:
            print(e)
            return Response({"generated_text": "Something went wrong. Please try again later."})
