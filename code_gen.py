import streamlit as st
import requests

def render():
    st.header("🎨 AI Code Generator")
    task = st.text_area("What code do you need?")
    lang = st.selectbox("Language", ["Python", "JavaScript", "Java", "C++", "HTML/CSS"])
    
    if st.button("Generate Code") and task:
        with st.spinner("Writing code..."):
            prompt = f"Write {lang} code for: {task}. Only return code with brief comments."
            res = requests.post("http://localhost:11434/api/generate", json={
                "model": "llama3", "prompt": prompt, "stream": False
            })
            st.code(res.json()["response"], language=lang.lower())