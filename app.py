import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import time
from datetime import datetime

# ---------------- SETUP ----------------
st.set_page_config(page_title="AI Agent Pro", layout="wide")
load_dotenv()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "logs" not in st.session_state:
    st.session_state.logs = []

if "stats" not in st.session_state:
    st.session_state.stats = {
        "queries": 0,
        "notes": 0,
        "emails": 0
    }

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Agent Control Panel")

web_search = st.sidebar.toggle("🌐 Web Search", True)
notes = st.sidebar.toggle("📝 Save Notes", True)
email = st.sidebar.toggle("📧 Send Email", False)
functions = st.sidebar.toggle("🧮 Functions", True)

st.sidebar.divider()

col1, col2 = st.sidebar.columns(2)
col1.metric("Queries", st.session_state.stats["queries"])
col2.metric("Notes", st.session_state.stats["notes"])

col3, col4 = st.sidebar.columns(2)
col3.metric("Emails", st.session_state.stats["emails"])
col4.metric("Messages", len(st.session_state.messages))

# Clear chat
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.messages = []
    st.session_state.logs = []
    st.rerun()

# Export chat
def export_chat():
    return "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])

st.sidebar.download_button(
    "⬇️ Download Chat",
    export_chat(),
    file_name="chat_history.txt"
)

# ---------------- MAIN UI ----------------
st.title("🤖 AI Agent Pro")

st.caption("Multi-tool AI agent with memory, logs & actions")

# ---------------- CHAT DISPLAY ----------------
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        avatar = "🧑" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# ---------------- TOOL LOG PANEL ----------------
st.divider()
st.subheader("📊 Agent Activity Log")

log_container = st.container()

with log_container:
    if st.session_state.logs:
        for log in reversed(st.session_state.logs[-8:]):
            st.write(f"🕒 {log}")
    else:
        st.info("No tool activity yet.")

# ---------------- INPUT ----------------
user_input = st.chat_input("Ask your AI agent...")

# ---------------- AGENT LOGIC ----------------
if user_input:

    # update stats
    st.session_state.stats["queries"] += 1

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user", avatar="🧑"):
        st.write(user_input)

    # fake "thinking" animation
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            time.sleep(0.6)

        # simulate tool usage
        tool_msg = None

        if "email" in user_input.lower() and email:
            tool_msg = "📧 Email tool triggered"
            st.session_state.stats["emails"] += 1

        elif "note" in user_input.lower() and notes:
            tool_msg = "📝 Note saved"
            st.session_state.stats["notes"] += 1

        elif "calculate" in user_input.lower() and functions:
            tool_msg = "🧮 Function tool used"

        if tool_msg:
            st.session_state.logs.append(
                f"{datetime.now().strftime('%H:%M:%S')} - {tool_msg}"
            )

        # Groq response
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages
            )

            reply = response.choices[0].message.content

            # typing effect
            placeholder = st.empty()
            typed_text = ""

            for char in reply:
                typed_text += char
                time.sleep(0.01)
                placeholder.markdown(typed_text)

        except Exception as e:
            reply = f"Error: {e}"
            st.error(reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply
    })
