import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from deep_translator import GoogleTranslator
import re

#--------------------
# PAGE CONFIGURATION
#--------------------
st.set_page_config(page_title="BDL.AI - Master Brain", page_icon="🧠", layout="wide")

#--------------------
# CUSTOM CSS & ANIMATIONS
#--------------------
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stChatMessage { border-radius: 15px; padding: 10px; margin-bottom: 10px; }
    h1 { color: #00d4ff; text-align: center; text-shadow: 0 0 10px #00d4ff; }
    .rtl-container { direction: rtl; text-align: right; background-color: #1f2937; padding: 10px; border-radius: 10px; margin-top: 10px; color: #ffffff; border-right: 4px solid #00d4ff; }
    .pulse-container { display: flex; align-items: center; gap: 10px; font-weight: bold; color: #00ff00; margin-bottom: 20px; }
    .pulse-circle { width: 12px; height: 12px; background-color: #00ff00; border-radius: 50%; box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); } 70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); } 100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0); } }
    </style>
    """, unsafe_allow_html=True)

#--------------------
# INITIALIZE SESSION STATE
#--------------------
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "waiting_for_answer" not in st.session_state: st.session_state.waiting_for_answer = False
if "last_question" not in st.session_state: st.session_state.last_question = ""
if "messages" not in st.session_state: st.session_state.messages = []
# NEW: The Offline Waiting Room
if "offline_buffer" not in st.session_state: st.session_state.offline_buffer = []

#--------------------
# GOOGLE SHEETS CONNECTION
#--------------------
connection_status = "Offline"
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    connection_status = "Online"
except Exception:
    pass # Stay in Offline mode

def load_brain_data():
    if connection_status == "Online":
        return conn.read(ttl=0)
    return pd.DataFrame(columns=["question", "answer", "status", "timestamp"])

#--------------------
# SIDEBAR & OFFLINE SYNC
#--------------------
with st.sidebar:
    st.title("⚙️ BDL Settings")
    
    # Connection Indicator
    if connection_status == "Online":
        st.markdown('<div class="pulse-container"><div class="pulse-circle"></div><span>CLOUD CONNECTED</span></div>', unsafe_allow_html=True)
    else:
        st.error("📡 OFFLINE MODE ACTIVE")

    # Admin Login
    password_input = st.text_input("Admin Key", type="password")
    st.session_state.is_admin = (password_input == "admin123")

    # --- FEATURE: OFFLINE SYNC BUTTON ---
    if st.session_state.offline_buffer:
        st.warning(f"📦 {len(st.session_state.offline_buffer)} Lessons Waiting to Sync")
        if connection_status == "Online" and st.session_state.is_admin:
            if st.button("🚀 Sync to Cloud Now"):
                df = load_brain_data()
                new_data = pd.DataFrame(st.session_state.offline_buffer)
                updated_df = pd.concat([df, new_data], ignore_index=True)
                conn.update(data=updated_df)
                st.session_state.offline_buffer = []
                st.success("Cloud Updated!")
                st.rerun()
        elif not st.session_state.is_admin:
            st.info("Login as Admin to Sync Cloud.")
    
    st.markdown("---")
    hebrew_mode = st.toggle("🇮🇱 Hebrew Mode", value=False)
    if st.button("Clear Chat UI"):
        st.session_state.messages = []
        st.rerun()

#--------------------
# MAIN BRAIN LOGIC
#--------------------
if prompt := st.chat_input("Ask BDL..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    response = ""

    # --- BLOCK 0: CALCULATOR ---
    if re.match(r"^[\d\+\-\*\/\(\)\s\.]+$", prompt.strip()):
        try: response = f"🔢 **Result:** {pd.eval(prompt)}"
        except: pass

    # --- BLOCK 1: LEARNING (OFFLINE FRIENDLY) ---
    elif st.session_state.waiting_for_answer:
        # Prepare the lesson metadata
        lesson = {
            "question": st.session_state.last_question.lower(),
            "answer": prompt,
            "status": "verified" if st.session_state.is_admin else "pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save to local buffer
        st.session_state.offline_buffer.append(lesson)
        response = "💾 **Saved Locally.** I'll remember this until we sync to the cloud!"
        st.session_state.waiting_for_answer = False

    # --- BLOCK 2: RETRIEVAL ---
    else:
        from thefuzz import process, fuzz
        # Check cloud + local buffer
        df = load_brain_data()
        local_df = pd.DataFrame(st.session_state.offline_buffer)
        full_brain = pd.concat([df, local_df], ignore_index=True)
        
        # Only search verified or locally added stuff
        questions = full_brain['question'].fillna('').tolist()
        
        if questions:
            best_match, score = process.extractOne(prompt, questions, scorer=fuzz.token_sort_ratio)
            if score >= 85:
                response = full_brain[full_brain['question'] == best_match].iloc[0]['answer']
        
        if not response:
            response = "I don't know that yet. **What is the answer?**"
            st.session_state.waiting_for_answer = True
            st.session_state.last_question = prompt

    # --- FINAL: HEBREW WRAP ---
    if hebrew_mode and response and "Result:" not in response:
        try:
            translated = GoogleTranslator(source='auto', target='iw').translate(response)
            response = f"{response}\n\n<div class='rtl-container'>🇮🇱 {translated}</div>"
        except: pass

    with st.chat_message("assistant"):
        st.markdown(response, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": response})
