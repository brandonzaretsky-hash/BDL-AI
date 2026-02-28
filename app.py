import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from deep_translator import GoogleTranslator
from thefuzz import process, fuzz
from gtts import gTTS
import io
import re

#--------------------
# Section 1: Page Configuration & Global Styles
#--------------------
st.set_page_config(page_title="BDL.AI - Master Brain", page_icon="🧠", layout="wide")

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
# Section 2: Global Variable & Session Initialization
#--------------------
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "waiting_for_answer" not in st.session_state: st.session_state.waiting_for_answer = False
if "last_question" not in st.session_state: st.session_state.last_question = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "offline_buffer" not in st.session_state: st.session_state.offline_buffer = []

#--------------------
# Section 3: Database Connection & Data Loading
#--------------------
connection_status = "Offline"
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
    connection_status = "Online"
except Exception:
    df = pd.DataFrame(columns=["question", "answer", "status", "timestamp"])

def load_fresh_data():
    if connection_status == "Online":
        return conn.read(ttl=0)
    return pd.DataFrame(columns=["question", "answer", "status", "timestamp"])

#--------------------
# Section 4: Sidebar - Access Control & Admin Login
#--------------------
with st.sidebar:
    st.title("🔐 Master Control")
    password_input = st.text_input("Admin Key", type="password")
    st.session_state.is_admin = (password_input == "admin123")

    if st.session_state.is_admin:
        st.markdown('<div class="pulse-container"><div class="pulse-circle"></div><span>ADMIN: ONLINE</span></div>', unsafe_allow_html=True)
    else:
        st.info("User Mode: Suggestions sent to Admin for review.")
    
    st.markdown("---")
    hebrew_mode = st.toggle("🇮🇱 Hebrew Practice Mode")
    
    if st.button("Clear Visual Chat History"):
        st.session_state.messages = []
        st.rerun()

#--------------------
# Section 5: Sidebar - Maintenance & Diagnostics
#--------------------
if st.session_state.is_admin:
    with st.sidebar:
        st.markdown("---")
        st.subheader("🛠️ Brain Maintenance")
        
        # Auto-Fixer
        if st.button("🧹 Auto-Fix: Clear Blank Rows"):
            df_clean = df.dropna(subset=['question', 'answer'], how='any')
            df_clean = df_clean[df_clean['question'].str.strip() != ""]
            if connection_status == "Online":
                conn.update(data=df_clean)
                st.success("Cloud Brain Cleaned!")
                st.rerun()

        # System Diagnostic
        if st.button("🚀 Run System Stress Test"):
            with st.status("Testing Systems...", expanded=True) as s:
                st.write("Math...")
                if pd.eval("100+50") == 150: st.success("✅ Math Passed")
                
                st.write("Translation...")
                try:
                    t = GoogleTranslator(source='en', target='iw').translate("Test")
                    st.success(f"✅ Hebrew: {t}")
                except: st.error("❌ Translation Fail")

                st.write("Speech...")
                try:
                    tts = gTTS("Test", lang='en')
                    st.success("✅ Speech Ready")
                except: st.error("❌ gTTS Fail")
                s.update(label="Test Complete", state="complete")

#--------------------
# Section 6: Sidebar - Moderation & Analytics
#--------------------
if st.session_state.is_admin:
    with st.sidebar:
        st.markdown("---")
        # Moderation
        pending_df = df[df['status'] == 'pending'] if 'status' in df.columns else pd.DataFrame()
        if not pending_df.empty:
            st.warning(f"🔔 {len(pending_df)} New Requests")
            for index, row in pending_df.iterrows():
                with st.expander(f"Q: {row['question'][:10]}"):
                    st.write(f"A: {row['answer']}")
                    if st.button("✅ Approve", key=f"app_{index}"):
                        df.at[index, 'status'] = 'verified'
                        conn.update(data=df); st.rerun()

        # Analytics
        if not df.empty and 'timestamp' in df.columns:
            st.markdown("### 📊 Growth")
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            st.bar_chart(df.groupby('date').size())

#--------------------
# Section 7: Sidebar - Data Sync & Backup
#--------------------
with st.sidebar:
    st.markdown("---")
    # Offline Sync
    if st.session_state.offline_buffer:
        st.warning(f"📦 {len(st.session_state.offline_buffer)} Offline Items")
        if st.session_state.is_admin and connection_status == "Online":
            if st.button("🚀 Sync to Cloud"):
                new_data = pd.DataFrame(st.session_state.offline_buffer)
                updated_df = pd.concat([df, new_data], ignore_index=True)
                conn.update(data=updated_df)
                st.session_state.offline_buffer = []
                st.success("Sync Complete!")
                st.rerun()

    # Backup Button
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Backup", csv, "BDL_Brain.csv", "text/csv")

#--------------------
# Section 8: Main UI Header & Message Display
#--------------------
st.title("🧠 BDL.AI - Master Brain")
st.caption(f"Status: {connection_status} | v3.1")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

#--------------------
# Section 9: Logic - Input & Calculator
#--------------------
if prompt := st.chat_input("Communicate..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    response = ""
    if re.match(r"^[\d\+\-\*\/\(\)\s\.]+$", prompt.strip()):
        try: response = f"🔢 **Result:** {pd.eval(prompt)}"
        except: pass

#--------------------
# Section 10: Logic - Learning & Moderation
#--------------------
    if not response and st.session_state.waiting_for_answer:
        lesson = {
            "question": st.session_state.last_question.lower(),
            "answer": prompt,
            "status": "verified" if st.session_state.is_admin else "pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.offline_buffer.append(lesson)
        response = "✅ Lesson Saved! (Stored for review)"
        st.session_state.waiting_for_answer = False

#--------------------
# Section 11: Logic - Smart Retrieval & Fuzzy Match
#--------------------
    elif not response:
        current_df = load_fresh_data()
        local_df = pd.DataFrame(st.session_state.offline_buffer)
        full_brain = pd.concat([current_df, local_df], ignore_index=True)
        
        valid_brain = full_brain[(full_brain['status'] == 'verified') | (full_brain.index >= len(current_df))]
        questions = valid_brain['question'].fillna('').tolist()
        
        if questions:
            best_match, score = process.extractOne(prompt, questions, scorer=fuzz.token_sort_ratio)
            if score >= 85:
                response = valid_brain[valid_brain['question'] == best_match].iloc[0]['answer']
        
        if not response:
            response = "I don't know that yet. **What is the answer?**"
            st.session_state.waiting_for_answer = True
            st.session_state.last_question = prompt

#--------------------
# Section 12: Logic - Hebrew RTL & Audio Support
#--------------------
    if hebrew_mode and response and "Result:" not in response:
        try:
            trans = GoogleTranslator(source='auto', target='iw').translate(response)
            response = f"{response}\n\n<div class='rtl-container'>🇮🇱 {trans}</div>"
        except: pass

    with st.chat_message("assistant"):
        st.markdown(response, unsafe_allow_html=True)
    st.session_state.messages.append({"role": "assistant", "content": response})
