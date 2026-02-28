import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from deep_translator import GoogleTranslator # Feature: Hebrew Support
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
    /* FEATURE FIX: Right-to-Left (RTL) Support for Hebrew */
    .rtl-text {
        direction: RTL;
        unicode-bidi: bidi-override;
        text-align: right;
        font-family: 'Arial', sans-serif;
        font-size: 1.2rem;
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

#--------------------
# GOOGLE SHEETS CONNECTION
#--------------------
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    connection_status = "Online"
except Exception:
    connection_status = "Offline"
    st.error("Connection failed.")
    st.stop()

def load_brain_data():
    return conn.read(ttl=0)

#--------------------
# SIDEBAR & SETTINGS
#--------------------
with st.sidebar:
    st.title("⚙️ BDL Settings")
    
    # 1. ADMIN LOGIN
    password_input = st.text_input("Admin Key", type="password")
    
    if password_input == "admin123":
        st.session_state.is_admin = True
        st.markdown('<div class="pulse-container"><div class="pulse-circle"></div><span>ADMIN: ONLINE</span></div>', unsafe_allow_html=True)
        df = load_brain_data()
        
        # FEATURE: CONFIDENCE SLIDER
        st.markdown("---")
        st.write("🧠 **Sensitivity**")
        confidence_level = st.slider("Strictness", 50, 100, 85, help="Low = Loose matching, High = Exact words only.")
        
        # --- MODERATION PANEL ---
        pending_df = df[df['status'] == 'pending'] if 'status' in df.columns else pd.DataFrame()
        if not pending_df.empty:
            st.warning(f"🔔 {len(pending_df)} Pending")
            st.components.v1.html("<audio autoplay><source src='https://www.soundjay.com/buttons/sounds/button-3.mp3'></audio>", height=0)
            for index, row in pending_df.iterrows():
                with st.expander(f"Q: {row['question'][:10]}"):
                    st.write(f"A: {row['answer']}")
                    if st.button("✅ Approve", key=f"app_{index}"):
                        df.at[index, 'status'] = 'verified'
                        conn.update(data=df)
                        st.rerun()
    else:
        st.session_state.is_admin = False
        confidence_level = 85 # Default for users
        st.info("User Mode Active")

    # FEATURE: HEBREW TRANSLATOR TOGGLE
    st.markdown("---")
    hebrew_mode = st.toggle("🇮🇱 Translate to Hebrew", value=False)
    
    if st.button("Clear Chat UI"):
        st.session_state.messages = []
        st.rerun()

#--------------------
# THE MASTER BRAIN LOGIC
#--------------------
if prompt := st.chat_input("Ask BDL..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    response = ""

    # --- BLOCK 0: CALCULATOR ---
    if re.match(r"^[\d\+\-\*\/\(\)\s\.]+$", prompt.strip()):
        try: response = f"🔢 **Result:** {pd.eval(prompt)}"
        except: pass

    # --- BLOCK 1: FORGET (ADMIN ONLY) ---
    if not response and prompt.lower().strip() == "forget that" and st.session_state.is_admin:
        df = load_brain_data()
        if not df.empty:
            last_q = df.iloc[-1]['question']
            conn.update(data=df.drop(df.tail(1).index))
            response = f"🗑️ Forgotten: '{last_q}'"

    # --- BLOCK 2: LEARNING ---
    elif not response and st.session_state.waiting_for_answer:
        df = load_brain_data()
        status = "verified" if st.session_state.is_admin else "pending"
        new_row = pd.DataFrame([{
            "question": st.session_state.last_question.lower(), 
            "answer": prompt, 
            "status": status,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        conn.update(data=pd.concat([df, new_row], ignore_index=True))
        response = "✅ Learned!" if st.session_state.is_admin else "📩 Sent for review."
        st.session_state.waiting_for_answer = False

    # --- BLOCK 3: SMART RETRIEVAL (WITH SLIDER & HEBREW) ---
    elif not response:
        from thefuzz import process, fuzz
        df = load_brain_data()
        verified_df = df[df['status'] == 'verified'] if 'status' in df.columns else df
        questions = verified_df['question'].fillna('').tolist()
        
        if questions:
            best_match, score = process.extractOne(prompt, questions, scorer=fuzz.token_sort_ratio)
            if score >= confidence_level:
                response = verified_df[verified_df['question'] == best_match].iloc[0]['answer']
        
        if not response:
            response = "I don't know that. What is the answer?"
            st.session_state.waiting_for_answer = True
            st.session_state.last_question = prompt

    # --- FINAL STEP: HEBREW TRANSLATION (FIXED RTL) ---
    if hebrew_mode and response and "Result:" not in response:
        try:
            translator = GoogleTranslator(source='auto', target='iw')
            hebrew_translation = translator.translate(response)
            
            # This HTML wrap ensures the Hebrew isn't backwards or left-aligned
            hebrew_html = f'<div class="rtl-text">🇮🇱 {hebrew_translation}</div>'
            response = f"{response}\n\n{hebrew_html}"
        except:
            response = f"{response}\n\n⚠️ Translation failed."
