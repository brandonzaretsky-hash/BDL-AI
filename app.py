import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fuzzywuzzy import fuzz, process
from deep_translator import GoogleTranslator
from gtts import gTTS
from streamlit_lottie import st_lottie
import io, re, wikipedia, wikipediaapi, time, requests
from datetime import datetime

#--------------------
# Section 0: Splash Animation (Robotic Brain)
#--------------------
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

# This is a high-tech robotic assembly animation
lottie_brain = load_lottieurl("https://lottie.host/8040d6c1-9031-4e76-9051-177b966b96e4/ZzQoUvV6wZ.json")

if "has_run_splash" not in st.session_state: st.session_state.has_run_splash = False

def run_brain_assembly():
    if not st.session_state.has_run_splash:
        splash_container = st.empty()
        with splash_container.container():
            st.markdown("<h2 style='text-align: center; color: #4CAF50;'>Assembling BDL.AI Cortex...</h2>", unsafe_allow_html=True)
            st_lottie(lottie_brain, height=400, key="initial_assembly")
            time.sleep(3) # Let the robotic arms finish the work
            st.toast("Brain Pulse: GREEN. Connection Established.")
            time.sleep(1)
        splash_container.empty()
        st.session_state.has_run_splash = True

#--------------------
# Section 1: Setup & CSS
#--------------------
st.set_page_config(page_title="BDL.AI Master Brain", layout="wide", page_icon="🧠")

st.markdown("""
    <style>
    .online-indicator { display: flex; align-items: center; justify-content: flex-end; color: #4CAF50; font-weight: bold; padding: 10px; }
    .dot { height: 10px; width: 10px; background-color: #4CAF50; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 8px #4CAF50; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 0.4; transform: scale(0.9); } 50% { opacity: 1; transform: scale(1.1); } 100% { opacity: 0.4; transform: scale(0.9); } }
    .rtl-container { direction: rtl; text-align: right; background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

# Run the robotic assembly animation
run_brain_assembly()

# Top Indicator
st.markdown('<div class="online-indicator"><span class="dot"></span>BDL.AI Online</div>', unsafe_allow_html=True)

# Session States
if "messages" not in st.session_state: st.session_state.messages = []
if "waiting_for_answer" not in st.session_state: st.session_state.waiting_for_answer = False
if "last_question" not in st.session_state: st.session_state.last_question = ""
if "last_mem_count" not in st.session_state: st.session_state.last_mem_count = 0

#--------------------
# Section 2: BDL.AI Setting Panel
#--------------------
with st.sidebar:
    st.title("⚙️ BDL.AI Setting Panel")
    access_key = st.text_input("Access Key", type="password")
    is_speak_role = (access_key == "qwerty")
    is_admin_role = (access_key == "admin") or is_speak_role 
    
    st.markdown("### 🧠 Universal Settings")
    st.session_state.deepthink_enabled = st.toggle("🌐 Deepthink Mode (Internet)", value=True)
    intel_level = st.slider("Intelligence Sensitivity", 50, 100, 85)
    hebrew_mode = st.toggle("🇮🇱 Hebrew Mode")
    voice_mode = st.toggle("🔊 Voice Response")
    
    conn = st.connection("gsheets", type=GSheetsConnection)

    if is_admin_role:
        st.markdown("---")
        st.markdown("### 👮 Admin Control")
        sport_mode = st.toggle("🏒 Sport Mode")
        try:
            pending_df = conn.read(worksheet="Requests", ttl="1s")
            if not pending_df.empty:
                st.dataframe(pending_df, use_container_width=True)
                req_idx = st.number_input("ID to Manage", 0, len(pending_df)-1, 0)
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Approve Lesson"):
                        main_mem = conn.read(worksheet="Memory", ttl="1s")
                        approved = pending_df.iloc[[req_idx]][['question', 'answer']]
                        conn.update(worksheet="Memory", data=pd.concat([main_mem, approved], ignore_index=True))
                        conn.update(worksheet="Requests", data=pending_df.drop(pending_df.index[req_idx]))
                        st.session_state.has_run_splash = False # Reset splash to show brain assembly again
                        st.rerun()
                with c2:
                    if st.button("❌ Decline Lesson"):
                        conn.update(worksheet="Requests", data=pending_df.drop(pending_df.index[req_idx]))
                        st.rerun()
        except: pass

    if st.button("🗑️ Reset Cortex"):
        st.session_state.messages = []
        st.rerun()

# [Sections 3-10 remain exactly as in V6.4 for Data, Math, Translation, and Deepthink logic]
# (Section 3: Data Write, Section 4: History, Section 5: Math, Section 6: Translation, 
# Section 7: Voice, Section 8: UI Helpers, Section 9: Deepthink, Section 10: Local Read)

# (Add your logic functions here as they were before...)

#--------------------
# Section 11: Logic - Deepthink Mode
#--------------------
if prompt := st.chat_input("Communicate with BDL.AI Master Brain..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    response = ""
    he_t = ""

    if st.session_state.waiting_for_answer:
        if is_speak_role:
            save_direct(st.session_state.last_question, prompt)
            response = "⚡ **Cortex Updated.** Knowledge added."
        else:
            save_request(st.session_state.last_question, prompt)
            response = "📝 **Lesson Queued.** Waiting for Admin approval."
        st.session_state.waiting_for_answer = False

    if not response: response = run_math(prompt)

    if not response and st.session_state.deepthink_enabled:
        with st.status("🧠 Deepthinking...", expanded=False) as s:
            # Note: Deepthink logic goes out to Wikipedia/Internet
            response = run_deepthink(prompt, summarize=("(summary)" in prompt.lower() or (is_admin_role and sport_mode)))
            s.update(label="Deepthink Scan Complete!", state="complete")

    if not response:
        try:
            df = conn.read(worksheet="Memory", ttl="1s")
            qs = df['question'].fillna('').tolist()
            if qs:
                match, score = process.extractOne(prompt, qs, scorer=fuzz.token_sort_ratio)
                if score >= intel_level: response = df[df['question'] == match].iloc[-1]['answer']
        except: pass

    if not response:
        response = "I haven't learned that yet. **What is the answer?**"
        st.session_state.waiting_for_answer = True
        st.session_state.last_question = prompt

    if response:
        if hebrew_mode and "Result:" not in response: he_t = get_hebrew(response)
        full = response + (f"\n\n---\n<div class='rtl-container'>🇮🇱 {he_t}</div>" if he_t else "")
        with st.chat_message("assistant"):
            st.markdown(full, unsafe_allow_html=True)
            if voice_mode: show_voices(response, he_t)
        st.session_state.messages.append({"role": "assistant", "content": full})
