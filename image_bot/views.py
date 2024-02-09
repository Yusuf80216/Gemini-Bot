from rest_framework.decorators import api_view
import google.generativeai as genai
from rest_framework.response import Response
from PIL import Image
from decouple import config
import os

API_KEY = config("GEMINI_API_KEY")

# Model Initialization
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro-vision')

@api_view(['POST'])
def image_bot(request):
    if request.method == 'POST':
        try:
            session_id = request.data.get('session_id')
            system_prompt = request.data.get('system_prompt', '')
            prompt = request.data.get('prompt')
            image = request.data.get('image')

            os.makedirs('image_bot/images/', exist_ok=True)
            with open(f"image_bot/images/{session_id}.png", 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)

            img = Image.open(f"image_bot/images/{session_id}.png")
            
            response = model.generate_content([system_prompt,
                                            prompt,
                                            img])
            response.resolve()
            os.remove(f"image_bot/images/{session_id}.png")

            return Response({'generated_text': response.text})
        except Exception as e:
            print(e)
            return Response({"generated_text": "Something went wrong. Please try again later."})