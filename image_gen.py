import streamlit as st
import requests
from urllib.parse import quote

def render():
    st.header("🖼️ AI Image Generator (Free)")
    prompt = st.text_input("Describe your image")
    
    if st.button("Generate 🎨") and prompt:
        with st.spinner("Creating image..."):
            # Free API (No key required)
            safe_prompt = quote(prompt)
            img_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true"
            
            st.image(img_url, caption=prompt)