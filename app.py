#--------------------
#Section 1 Setup and Role Logic
#--------------------
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fuzzywuzzy import fuzz, process
from deep_translator import GoogleTranslator
from gtts import gTTS
import io, re, wikipedia, wikipediaapi
from datetime import datetime

st.set_page_config(page_title="BDL-ai V5.4", layout="wide", page_icon="🤖")

if "messages" not in st.session_state: st.session_state.messages = []
if "waiting_for_answer" not in st.session_state: st.session_state.waiting_for_answer = False
if "last_question" not in st.session_state: st.session_state.last_question = ""
#--------------------
#Section 2 Sidebar Securety and Sheet Doctor
#--------------------
with st.sidebar:
    st.title("🛡️ BDL Access Control")
    access_key = st.text_input("Enter Access Key", type="password")

    is_speak_role = (access_key == "qwerty") # Super-Dev
    is_admin_role = (access_key == "admin") or is_speak_role # Admin
    
    # LEVEL 1: USER TOOLS
    st.markdown("### 🛠️ Basic Controls")
    intel_level = st.slider("🧠 Intelligence Level", 50, 100, 85)
    hebrew_mode = st.toggle("🇮🇱 Hebrew Mode")
    voice_mode = st.toggle("🔊 Voice Response")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    # LEVEL 2: ADMIN PANEL
    if is_admin_role:
        st.markdown("---")
        st.markdown("### 👮 Admin & Approvals")
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        try:
            pending_df = conn.read(worksheet="Requests", ttl="1s")
            if not pending_df.empty:
                st.dataframe(pending_df)
                req_idx = st.number_input("Approve Row ID", 0, len(pending_df)-1, 0)
                if st.button("✅ Approve"):
                    main_mem = conn.read(worksheet="Memory", ttl="1s")
                    approved = pending_df.iloc[[req_idx]][['question', 'answer']]
                    updated_main = pd.concat([main_mem, approved], ignore_index=True)
                    conn.update(worksheet="Memory", data=updated_main)
                    new_pending = pending_df.drop(pending_df.index[req_idx])
                    conn.update(worksheet="Requests", data=new_pending)
                    st.success("Memory Authenticated!")
                    st.rerun()
            else: st.caption("No pending requests.")
        except:
            st.warning("⚠️ 'Requests' tab not found.")

    # LEVEL 3: SUPER-DEV & SHEET DOCTOR
    if is_speak_role:
        st.markdown("---")
        st.markdown("### ⚡ Super-Dev Tools")
        st.session_state.is_speak_mode = st.toggle("🌐 Internet Deep-Scan", value=True)
        
        if st.button("🩺 Run Sheet Doctor"):
            st.write("🔍 **Scanning Database Structure...**")
            tabs_found = []
            try:
                m_check = conn.read(worksheet="Memory", ttl="1s")
                tabs_found.append("✅ Memory Tab Found")
            except: tabs_found.append("❌ Memory Tab Missing")
            
            try:
                r_check = conn.read(worksheet="Requests", ttl="1s")
                tabs_found.append("✅ Requests Tab Found")
            except: tabs_found.append("❌ Requests Tab Missing")
            
            for status in tabs_found: st.write(status)
            
            if "❌" in str(tabs_found):
                st.error("Structure Error Detected!")
                st.write("Please ensure your Google Sheet has these tabs and headers:")
                st.code("Tab 1: Memory (Columns: question, answer)\nTab 2: Requests (Columns: question, answer, user, timestamp)")
#--------------------
#Section 3 Data Logic (Read/Write)
#--------------------
def save_direct(q, a):
    try:
        df = conn.read(worksheet="Memory", ttl="1s")
        new_row = pd.DataFrame([{"question": q.lower(), "answer": a}])
        conn.update(worksheet="Memory", data=pd.concat([df, new_row], ignore_index=True))
        st.success("⚡ Memory Saved.")
    except: st.error("Write Error.")

def save_request(q, a):
    try:
        df = conn.read(worksheet="Requests", ttl="1s")
        new_req = pd.DataFrame([{
            "question": q.lower(), "answer": a, 
            "user": "User", "timestamp": datetime.now().strftime("%H:%M")
        }])
        conn.update(worksheet="Requests", data=pd.concat([df, new_req], ignore_index=True))
    except: st.error("Requests tab missing! Run Sheet Doctor.")
#--------------------
#Section 4 Brain Engine
#--------------------
if prompt := st.chat_input("Communicate..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    response = ""
    hebrew_trans = ""

    # A. Teaching Logic
    if st.session_state.waiting_for_answer:
        if is_speak_role:
            save_direct(st.session_state.last_question, prompt)
            response = "⚡ Super-Dev Override: Data Stored."
        else:
            save_request(st.session_state.last_question, prompt)
            response = "📝 Lesson logged for Admin review."
        st.session_state.waiting_for_answer = False

    # B. Read Logic
    if not response:
        # Internet Brain (Speak Only)
        if st.session_state.get('is_speak_mode'):
            # (Wikipedia code from V5.1 here)
            pass
        
        # Local Memory
        if not response:
            try:
                main_df = conn.read(worksheet="Memory", ttl="1s")
                questions = main_df['question'].fillna('').tolist()
                match, score = process.extractOne(prompt, questions, scorer=fuzz.token_sort_ratio)
                if score >= intel_level:
                    response = main_df[main_df['question'] == match].iloc[-1]['answer']
            except: pass

    if not response:
        response = "I haven't learned that yet. **What is the answer?**"
        st.session_state.waiting_for_answer = True
        st.session_state.last_question = prompt

    # Final Output
    if response:
        with st.chat_message("assistant"): st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    
