import streamlit as st
from PIL import Image
import requests
import uuid
from decouple import config

API_URL = config("API_URL")

st.sidebar.title("Google's Gemini")
system_prompt = st.sidebar.text_area("System Prompt:", value="You are a helpful AI Assistant.")
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

def chatbot(session_id):
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message['content'])

    prompt = st.chat_input("Message Gemini...")
    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Thinking..."):
            data = {'session_id': st.session_state.session_id, 'system_prompt': system_prompt, 'prompt': prompt}
            response = requests.post(f"{API_URL}/chat/", data=data)
            result = response.json()
            result = result['generated_text']

        with st.chat_message("assistant"):
            st.markdown(result)

        st.session_state.messages.append({"role": "assistant", "content": result})

def imagebot(session_id):
    uploaded_file = st.file_uploader("Please upload an image")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Your uploaded image', width=200)
        prompt = st.text_input(label="Ask about uploaded image...", key=session_id)
        if prompt is not None and st.button("Ask"):
            with st.spinner("Thinking..."):
                data = {'session_id': session_id,
                        'system_prompt': system_prompt,
                        'prompt': prompt,
                        }
                files = {'image': uploaded_file.getvalue()}
                response = requests.post(f"{API_URL}/image/", data=data, files=files)

            if response.status_code == 200:
                result = response.json()
                result = result['generated_text']
                st.markdown(result)
            else:
                st.error("Failed to send the data.")


def chat():
    chatbot(st.session_state.session_id)

def image():
    imagebot(st.session_state.session_id)

PAGES = {
    "ChatBot": chat,
    "ImageBot": image,
}

selection = st.sidebar.radio("", list(PAGES.keys()))
page = PAGES[selection]
page()
