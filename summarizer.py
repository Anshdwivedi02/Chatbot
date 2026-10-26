import streamlit as st
import requests

def render():
    st.header("📄 Text Summarizer")
    text = st.text_area("Paste text here", height=250)
    length = st.radio("Summary length", ["Short", "Medium", "Detailed"])
    
    if st.button("Summarize") and text:
        with st.spinner("Summarizing..."):
            prompt = f"Summarize this text in {length.lower()} form:\n\n{text}"
            res = requests.post("http://localhost:11434/api/generate", json={
                "model": "llama3", "prompt": prompt, "stream": False
            })
            st.write(res.json()["response"])