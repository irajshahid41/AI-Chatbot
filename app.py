import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
import time
from datetime import datetime

# ---------------- SETUP ----------------
st.set_page_config(page_title="AI Agent Workspace", layout="wide")
load_dotenv()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ---------------- SESSION STATE ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "logs" not in st.session_state:
    st.session_state.logs = []

if "pinned" not in st.session_state:
    st.session_state.pinned = []

if "stats" not in st.session_state:
    st.session_state.stats = {"queries": 0, "tools": 0}

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙️ Agent Controls")

mode = st.sidebar.radio("Mode", ["Chat", "Agent (Thinking Mode)", "Command Mode"])

web_search = st.sidebar.toggle("🌐 Web Tool", True)
notes_tool = st.sidebar.toggle("📝 Notes Tool", True)
email_tool = st.sidebar.toggle("📧 Email Tool", False)

st.sidebar.divider()

st.sidebar.metric("Queries", st.session_state.stats["queries"])
st.sidebar.metric("Tools Used", st.session_state.stats["tools"])
st.sidebar.metric("Pinned", len(st.session_state.pinned))

# Clear
if st.sidebar.button("🧹 Reset Workspace"):
    st.session_state.messages = []
    st.session_state.logs = []
    st.session_state.pinned = []
    st.rerun()

# ---------------- HEADER ----------------
st.title("🤖 AI Agent Workspace")
st.caption("A multi-mode interactive AI system (Chat + Agent + Commands)")

# ---------------- Pinned Messages ----------------
with st.expander("📌 Pinned Context", expanded=False):
    if st.session_state.pinned:
        for p in st.session_state.pinned:
            st.info(p)
    else:
        st.write("No pinned items")

# ---------------- CHAT DISPLAY ----------------
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        col1, col2 = st.columns([1, 10])
        with col1:
            if msg["role"] == "assistant":
                if st.button("📌", key=f"pin_{i}"):
                    st.session_state.pinned.append(msg["content"])

# ---------------- COMMAND BAR ----------------
st.divider()
command = st.text_input("⚡ Command Bar (try /clear, /export, /note, /mode)")

if command:
    if command == "/clear":
        st.session_state.messages = []
        st.session_state.logs = []
        st.success("Workspace cleared")
        st.rerun()

    elif command == "/export":
        st.download_button(
            "Download Chat",
            "\n".join([m["content"] for m in st.session_state.messages]),
            file_name="chat.txt"
        )

    elif command.startswith("/note"):
        note = command.replace("/note", "").strip()
        st.session_state.pinned.append("📝 " + note)
        st.success("Note saved!")

    elif command.startswith("/mode"):
        st.info("Switch mode from sidebar")

# ---------------- AGENT THINKING VIEW ----------------
def agent_thinking(query):
    steps = [
        "Analyzing input...",
        "Checking tools availability...",
        "Processing context...",
        "Generating response..."
    ]

    for step in steps:
        st.write("🧠 " + step)
        time.sleep(0.3)

# ---------------- INPUT ----------------
user_input = st.chat_input("Ask your AI Agent...")

if user_input:
    st.session_state.stats["queries"] += 1

    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):

        if mode == "Agent (Thinking Mode)":
            agent_thinking(user_input)

        # tool simulation
        tool_used = None

        if "note" in user_input.lower() and notes_tool:
            tool_used = "📝 Notes tool activated"
        elif "email" in user_input.lower() and email_tool:
            tool_used = "📧 Email tool activated"
        elif "search" in user_input.lower() and web_search:
            tool_used = "🌐 Web tool activated"

        if tool_used:
            st.session_state.logs.append(
                f"{datetime.now().strftime('%H:%M:%S')} - {tool_used}"
            )
            st.session_state.stats["tools"] += 1
            st.toast(tool_used)

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=st.session_state.messages
            )

            reply = response.choices[0].message.content

            # streaming effect
            box = st.empty()
            output = ""

            for c in reply:
                output += c
                time.sleep(0.005)
                box.markdown(output)

        except Exception as e:
            reply = f"Error: {e}"
            st.error(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# ---------------- ACTIVITY CONSOLE ----------------
st.divider()
st.subheader("📊 Live Agent Console")

with st.container():
    for log in reversed(st.session_state.logs[-10:]):
        st.code(log)
