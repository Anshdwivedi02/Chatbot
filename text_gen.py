import streamlit as st
import requests

def render():
    st.header("📝 AI Text Generator")
    
    content_type = st.selectbox("Type", ["Blog", "Email", "Instagram Caption", "Story"])
    topic = st.text_input("Topic / Prompt")
    tone = st.selectbox("Tone", ["Professional", "Casual", "Funny", "Formal"])
    
    if st.button("Generate ✨") and topic:
        with st.spinner("Generating..."):
            prompt = f"Write a {content_type} about '{topic}' in {tone} tone."
            res = requests.post("http://localhost:11434/api/generate", json={
                "model": "llama3", "prompt": prompt, "stream": False
            })
            output = res.json()["response"]
            st.markdown(output)
            st.download_button("Download", output, "output.txt")