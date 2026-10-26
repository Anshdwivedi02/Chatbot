import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# API key load karo
load_dotenv()

# Groq ke API endpoint aur key ka use
client = OpenAI(
    api_key="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",  # <--- Aapki asli key yahan aayegi
    base_url="https://api.groq.com/openai/v1"
)

# Knowledge Base (Dummy Store Data)
faq_data = """
Store Name: TechGadgets
Return Policy: Items can be returned within 30 days of purchase. Original packaging required.
Shipping: We ship internationally to USA, UK, and Canada. Standard shipping takes 5-7 business days.
Contact: support@techgadgets.com
"""

# AI ko instruction (System Prompt)
system_prompt = f"""
You are a helpful customer support assistant for TechGadgets.
Answer the user's question ONLY using the information provided below.
If the answer is not in the information, politely say: "I'm sorry, I don't have that information. Please contact support@techgadgets.com."

Information:
{faq_data}
"""

def chat_with_bot(user_question):
    response = client.chat.completions.create(
        # Groq ka free aur fast model
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ],
        temperature=0.2 
    )
    return response.choices[0].message.content

# --- Streamlit UI ---
st.title("🛍️ TechGadgets Support Bot")
st.caption("Ask me about returns, shipping, or contact info.")

# Chat history save karne ke liye
if "messages" not in st.session_state:
    st.session_state.messages = []

# Purane messages dikhana
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Naya input lena
if prompt := st.chat_input("Type your question here..."):
    # User ka message save aur show karo
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Bot ka reply generate karo
    with st.chat_message("assistant"):
        response = chat_with_bot(prompt)
        st.markdown(response)
    
    # Bot ka message save karo
    st.session_state.messages.append({"role": "assistant", "content": response})