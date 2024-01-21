import streamlit as st
import google.generativeai as genai
from decouple import config
import requests
import uuid

API_URL = "http://127.0.0.1:9000"

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if 'show_sidebar' not in st.session_state:
    st.session_state.show_sidebar = True

if st.session_state.show_sidebar:
    st.session_state.show_sidebar = False

    system_prompt = st.sidebar.text_area("Enter System Prompt...")

if not st.session_state.show_sidebar:
    st.session_state.show_sidebar = True

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

    data = {'session_id': st.session_state.session_id, 'system_prompt': system_prompt, 'prompt': prompt}
    response = requests.post(f"{API_URL}/chat/", data=data)
    result = response.json()
    result = result['generated_text']

    with st.chat_message("assistant"):
        st.markdown(result)

    st.session_state.messages.append({"role": "assistant", "content": result})
