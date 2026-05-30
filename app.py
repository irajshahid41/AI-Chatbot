import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

# ---------------- SETUP ----------------
st.set_page_config(page_title="AI Agent", layout="wide")
load_dotenv()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Agent Tools")

web_search = st.sidebar.toggle("🌐 Web Search", value=True)
notes = st.sidebar.toggle("📝 Save Notes", value=True)
email = st.sidebar.toggle("📧 Send Email", value=False)
functions = st.sidebar.toggle("🧮 Functions", value=True)

st.sidebar.divider()
st.sidebar.write("📊 Status")
st.sidebar.write("Queries run: 0")
st.sidebar.write("Notes saved: 0")
st.sidebar.write("Emails sent: 0")

# ---------------- MAIN UI ----------------
st.title("🤖 AI Agent Chatbot")

# session memory
if "messages" not in st.session_state:
    st.session_state.messages = []

# show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# input box
user_input = st.chat_input("Ask something...")

# ---------------- CHAT LOGIC ----------------
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=st.session_state.messages
        )

        reply = response.choices[0].message.content

        st.session_state.messages.append({"role": "assistant", "content": reply})

        with st.chat_message("assistant"):
            st.write(reply)

    except Exception as e:
        st.error(f"Error: {e}")
 
# ---------------- RIGHT PANEL ----------------
st.divider()
st.subheader("📊 Tool Log")
st.info("Tool log is empty.")
