import streamlit as st
import requests
import json
from urllib.parse import quote
from streamlit_mic_recorder import speech_to_text
import database as db
import pypdf

st.set_page_config(page_title="AI Studio Pro", page_icon="🤖", layout="wide")
st.title("🤖 AI Studio - Pro Version")

# Initialize DB
db.init_db()

# Initialize Session State
if "current_session" not in st.session_state:
    st.session_state.current_session = None

# ==========================================
# SIDEBAR (ChatGPT Style History)
# ==========================================
st.sidebar.header("⚙️ AI Studio Menu")
option = st.sidebar.radio("Select Feature", ["💬 Chatbot", "📝 Text Generator", "🖼️ Image Generator", "📄 Summarizer", "🎨 Code Generator"])

if option == "💬 Chatbot":
    st.sidebar.markdown("---")
    if st.sidebar.button("➕ New Chat"):
        st.session_state.current_session = db.create_session()
        st.rerun()
    
    st.sidebar.subheader("History")
    sessions = db.get_all_sessions()
    for sess_id, title in sessions:
        col1, col2 = st.sidebar.columns([4, 1])
        if col1.button(f"💬 {title[:15]}...", key=sess_id):
            st.session_state.current_session = sess_id
            st.rerun()
        if col2.button("🗑️", key=f"del_{sess_id}"):
            db.delete_session(sess_id)
            if st.session_state.current_session == sess_id:
                st.session_state.current_session = None
            st.rerun()

# ==========================================
# FEATURE 1: CHATBOT (Streaming + History + PDF)
# ==========================================
if option == "💬 Chatbot":
    st.header("💬 AI Chatbot (ChatGPT Style)")
    
    if st.session_state.current_session is None:
        st.info("👈 Sidebar se 'New Chat' par click karein ya purani chat select karein.")
    else:
        session_id = st.session_state.current_session
        messages = db.load_messages(session_id)
        
        # PDF Uploader
        with st.expander("📄 Upload PDF (Is PDF se sawal poochein)"):
            pdf_file = st.file_uploader("Choose a PDF file", type="pdf")
            if pdf_file:
                reader = pypdf.PdfReader(pdf_file)
                pdf_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                st.success("PDF Loaded! Ab niche sawal poochein.")
                # Is text ko AI ke context me bhejenge

        # Display Chat History
        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Voice Input
        st.write("🎤 **Awaz mein bolein:**")
        text_from_voice = speech_to_text(language='en', start_prompt="🔴 Start Recording", stop_prompt="⏹️ Stop", just_once=True, use_container_width=True)
        
        prompt = text_from_voice if text_from_voice else None
        chat_input = st.chat_input("Type your message here...")
        if chat_input:
            prompt = chat_input

        if prompt:
            # Save User Msg
            db.save_message(session_id, "user", prompt)
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Update Session Title (if it's a new chat)
            if len(messages) == 0:
                conn = db.sqlite3.connect(db.DB_NAME)
                c = conn.cursor()
                c.execute("UPDATE sessions SET title = ? WHERE id = ?", (prompt[:20], session_id))
                conn.commit()
                conn.close()

            # API Call with Streaming
            with st.chat_message("assistant"):
                # Agar PDF hai, toh prompt me add karo
                if 'pdf_text' in locals() and pdf_text:
                    system_prompt = f"Use the following context to answer:\n{pdf_text}\n\nQuestion: {prompt}"
                    api_messages = messages + [{"role": "user", "content": system_prompt}]
                else:
                    api_messages = messages + [{"role": "user", "content": prompt}]

                res = requests.post("http://localhost:11434/api/chat", json={
                    "model": "phi3",
                    "messages": api_messages,
                    "stream": True
                }, stream=True)
                
                def stream_data():
                    for line in res.iter_lines():
                        if line:
                            chunk = json.loads(line)
                            if "message" in chunk:
                                yield chunk["message"]["content"]
                
                reply = st.write_stream(stream_data)
            
            # Save AI Msg
            db.save_message(session_id, "assistant", reply)

# ==========================================
# OTHER FEATURES
# ==========================================
elif option == "📝 Text Generator":
    st.header("📝 AI Text Generator")
    content_type = st.selectbox("Type", ["Blog", "Email", "Instagram Caption", "Story"])
    topic = st.text_input("Topic / Prompt")
    if st.button("Generate ✨") and topic:
        with st.spinner("Generating..."):
            res = requests.post("http://localhost:11434/api/generate", json={"model": "phi3", "prompt": f"Write a {content_type} about '{topic}'", "stream": False})
            st.markdown(res.json()["response"])

elif option == "🖼️ Image Generator":
    st.header("🖼️ AI Image Generator")
    prompt = st.text_input("Describe your image in English")
    if st.button("Generate 🎨") and prompt:
        with st.spinner("Creating image..."):
            img_url = f"https://image.pollinations.ai/prompt/{quote(prompt)}?width=1024&height=1024&nologo=true"
            st.image(img_url, caption=prompt)

elif option == "📄 Summarizer":
    st.header("📄 Text Summarizer")
    text = st.text_area("Paste text here", height=250)
    if st.button("Summarize") and text:
        with st.spinner("Summarizing..."):
            res = requests.post("http://localhost:11434/api/generate", json={"model": "phi3", "prompt": f"Summarize this:\n\n{text}", "stream": False})
            st.write(res.json()["response"])

elif option == "🎨 Code Generator":
    st.header("🎨 AI Code Generator")
    task = st.text_area("What code do you need?")
    lang = st.selectbox("Language", ["Python", "JavaScript", "Java", "C++"])
    if st.button("Generate Code") and task:
        with st.spinner("Writing code..."):
            res = requests.post("http://localhost:11434/api/generate", json={"model": "phi3", "prompt": f"Write {lang} code for: {task}. Only return code.", "stream": False})
            st.code(res.json()["response"], language=lang.lower())