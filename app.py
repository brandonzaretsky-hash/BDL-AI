import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from deep_translator import GoogleTranslator
from thefuzz import process, fuzz
import re
import base64

#--------------------
# PAGE CONFIGURATION
#--------------------
st.set_page_config(
    page_title="BDL.AI - Master Brain",
    page_icon="🧠",
    layout="wide"
)

#--------------------
# CUSTOM CSS & ANIMATIONS
#--------------------
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stChatMessage { border-radius: 15px; padding: 10px; margin-bottom: 10px; }
    h1 { color: #00d4ff; text-align: center; text-shadow: 0 0 10px #00d4ff; }
    
    /* RTL Hebrew Container */
    .rtl-container {
        direction: rtl;
        text-align: right;
        background-color: #1f2937;
        padding: 12px;
        border-radius: 10px;
        margin-top: 10px;
        color: #ffffff;
        border-right: 5px solid #00d4ff;
        font-family: 'Arial', sans-serif;
    }

    /* Pulsing Admin Light */
    .pulse-container { display: flex; align-items: center; gap: 10px; font-weight: bold; color: #00ff00; margin-bottom: 20px; }
    .pulse-circle {
        width: 12px; height: 12px; background-color: #00ff00; border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7);
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0); }
    }
    </style>
    """, unsafe_allow_html=True)

#--------------------
# INITIALIZE SESSION STATE
#--------------------
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "waiting_for_answer" not in st.session_state: st.session_state.waiting_for_answer = False
if "last_question" not in st.session_state: st.session_state.last_question = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "offline_buffer" not in st.session_state: st.session_state.offline_buffer = []

#--------------------
# GOOGLE SHEETS CONNECTION
#--------------------
connection_status = "Offline"
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    connection_status = "Online"
except Exception:
    pass # Reverts to Offline logic

def load_brain_data():
    if connection_status == "Online":
        return conn.read(ttl=0)
    return pd.DataFrame(columns=["question", "answer", "status", "timestamp"])

#--------------------
# SIDEBAR & MASTER CONTROL
#--------------------
with st.sidebar:
    st.title("🔐 Master Control")
    
    # 1. Connection & Pulse
    if connection_status == "Online":
        st.markdown('<div class="pulse-container"><div class="pulse-circle"></div><span>CLOUD SYNC ACTIVE</span></div>', unsafe_allow_html=True)
    else:
        st.error("📡 OFFLINE MODE")

    # 2. Admin Login
    password_input = st.text_input("Admin Key", type="password")
    if password_input == "admin123":
        st.session_state.is_admin = True
        st.success("Admin Authenticated")
        
        # Fresh Data Load for Admin
        df = load_brain_data()
        
        # FEATURE: CONFIDENCE SLIDER
        st.markdown("---")
        st.write("🧠 **Match Sensitivity**")
        conf_level = st.slider("Strictness", 50, 100, 85)

        # FEATURE: OFFLINE SYNC
        if st.session_state.offline_buffer:
            st.warning(f"📦 {len(st.session_state.offline_buffer)} Lessons Pending Sync")
            if st.button("🚀 Sync Offline Data"):
                new_data = pd.DataFrame(st.session_state.offline_buffer)
                updated_df = pd.concat([df, new_data], ignore_index=True)
                conn.update(data=updated_df)
                st.session_state.offline_buffer = []
                st.success("Cloud Updated!")
                st.rerun()

        # FEATURE: INDIVIDUAL MODERATION
        pending_df = df[df['status'] == 'pending'] if 'status' in df.columns else pd.DataFrame()
        if not pending_df.empty:
            st.markdown("---")
            st.warning(f"🔔 {len(pending_df)} Suggestions")
            # Audio Alert
            st.components.v1.html("<audio autoplay><source src='https://www.soundjay.com/buttons/sounds/button-3.mp3'></audio>", height=0)
            for index, row in pending_df.iterrows():
                with st.expander(f"Review: {row['question'][:15]}"):
                    st.write(f"**A:** {row['answer']}")
                    c1, c2 = st.columns(2)
                    if c1.button("✅", key=f"a_{index}"):
                        df.at[index, 'status'] = 'verified'
                        conn.update(data=df); st.rerun()
                    if c2.button("🗑️", key=f"d_{index}"):
                        conn.update(data=df.drop(index)); st.rerun()

        # FEATURE: ANALYTICS
        st.markdown("---")
        st.write("📊 **Brain Growth**")
        if not df.empty and 'timestamp' in df.columns:
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            st.bar_chart(df.groupby('date').size(), color="#00d4ff")
    else:
        st.session_state.is_admin = False
        conf_level = 85
        st.info("User Mode: Teaching sends suggestions to Admin.")

    st.markdown("---")
    hebrew_mode = st.toggle("🇮🇱 Hebrew Practice Mode")
    if st.button("Clear Chat Window"):
        st.session_state.messages = []
        st.rerun()

#--------------------
# MAIN CHAT UI
#--------------------
st.title("🧠 BDL.AI - Master Brain")
st.caption("v3.0 - The Complete Neural Engine")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

#--------------------
# THE BRAIN PROCESSING ENGINE
#--------------------
if prompt := st.chat_input("Communicate..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    response = ""
    
    # 1. CALCULATOR BLOCK
    if re.match(r"^[\d\+\-\*\/\(\)\s\.]+$", prompt.strip()):
        try: response = f"🔢 **Calculation:** {pd.eval(prompt)}"
        except: pass

    # 2. FORGET BLOCK (ADMIN ONLY)
    if not response and prompt.lower().strip() == "forget that" and st.session_state.is_admin:
        df = load_brain_data()
        if not df.empty:
            last_q = df.iloc[-1]['question']
            conn.update(data=df.drop(df.tail(1).index))
            response = f"🗑️ **Forgotten:** '{last_q}'"

    # 3. LEARNING BLOCK (OFFLINE/USER FRIENDLY)
    elif not response and st.session_state.waiting_for_answer:
        lesson = {
            "question": st.session_state.last_question.lower(),
            "answer": prompt,
            "status": "verified" if st.session_state.is_admin else "pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.offline_buffer.append(lesson)
        response = "✅ Lesson Received! (Stored for Moderation)"
        st.session_state.waiting_for_answer = False

    # 4. SMART RETRIEVAL BLOCK
    elif not response:
        df = load_brain_data()
        local_df = pd.DataFrame(st.session_state.offline_buffer)
        full_brain = pd.concat([df, local_df], ignore_index=True)
        
        # Only answer from Verified Cloud or Local session
        valid_brain = full_brain[(full_brain['status'] == 'verified') | (full_brain.index >= len(df))]
        questions = valid_brain['question'].fillna('').tolist()
        
        if questions:
            best_match, score = process.extractOne(prompt, questions, scorer=fuzz.token_sort_ratio)
            if score >= conf_level:
                response = valid_brain[valid_brain['question'] == best_match].iloc[0]['answer']
        
        if not response:
            response = "I don't know that yet. **What is the answer?**"
            st.session_state.waiting_for_answer = True
            st.session_state.last_question = prompt

    # 5. HEBREW RTL TRANSLATION
    if hebrew_mode and response and "Calculation:" not in response:
        try:
            trans = GoogleTranslator(source='auto', target='iw').translate(response)
            response = f"{response}\n\n<div class='rtl-container'>🇮🇱 {trans}</div>"
        except: pass

    # OUTPUT
    with st.chat_message("assistant"):
        st.markdown(response, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": response})
