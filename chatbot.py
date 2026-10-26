import streamlit as st
import requests
from streamlit_mic_recorder import speech_to_text

def render():
    st.header("💬 AI Chatbot (Voice + Text)")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mic Button
    st.write("🎤 **Awaz mein bolein (Speak in English/Hindi):**")
    text_from_voice = speech_to_text(
        language='en', 
        start_prompt="🔴 Start Recording", 
        stop_prompt="⏹️ Stop Recording", 
        just_once=True, 
        use_container_width=True
    )
    
    # Voice input ko prompt banao
    prompt = None
    if text_from_voice:
        prompt = text_from_voice
    
    # Chat history display karo
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Keyboard input
    chat_input = st.chat_input("Ya yahan type karein...")
    if chat_input:
        prompt = chat_input

    # Agar user ne kuch bola ya likha hai
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                res = requests.post("http://localhost:11434/api/chat", json={
                    "model": "llama3",
                    "messages": st.session_state.messages,
                    "stream": False
                })
                reply = res.json()["message"]["content"]
                st.markdown(reply)
        
        st.session_state.messages.append({"role": "assistant", "content": reply})