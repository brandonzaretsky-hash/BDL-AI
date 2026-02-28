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
# MAINTENANCE & DIAGNOSTICS (ADMIN ONLY)
#--------------------
if st.session_state.is_admin:
    st.markdown("---")
    st.subheader("🛠️ System Tools")
    
    # 1. THE AUTO-FIXER (FEATURE 2)
    if st.button("🧹 Auto-Fix: Clear Blank Rows"):
        with st.spinner("Cleaning Brain..."):
            try:
                df = load_brain_data()
                initial_count = len(df)
                
                # Remove rows that are completely empty or have NaN in Q/A
                df_clean = df.dropna(subset=['question', 'answer'], how='any')
                # Remove rows that just have whitespace
                df_clean = df_clean[df_clean['question'].str.strip() != ""]
                
                final_count = len(df_clean)
                removed = initial_count - final_count
                
                if removed > 0:
                    conn.update(data=df_clean)
                    st.success(f"Cleaned! Removed {removed} empty neural links.")
                else:
                    st.info("Brain is already healthy. No empty rows found.")
            except Exception as e:
                st.error(f"Cleaning Error: {e}")

    # 2. THE SYSTEM DIAGNOSTIC (STRESS TEST)
    if st.button("🚀 Run Full System Test"):
        with st.status("BDL Diagnostics: Running...", expanded=True) as status:
            
            # A. MATH TEST
            st.write("Testing Math Processor...")
            if pd.eval("150 * 2 + 50") == 350:
                st.success("✅ Math: 350 (Passed)")
            
            # B. HEBREW & RTL TEST
            st.write("Testing Hebrew Translation...")
            try:
                from deep_translator import GoogleTranslator
                test_trans = GoogleTranslator(source='en', target='iw').translate("Online")
                st.markdown(f'<div class="rtl-container">✅ Hebrew: {test_trans}</div>', unsafe_allow_html=True)
            except: st.error("❌ Hebrew: Service Timed Out")

            # C. SPEECH SYNTH TEST
            st.write("Testing Speech Synth...")
            try:
                from gtts import gTTS
                import io
                tts = gTTS("System Operational", lang='en')
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp, format='audio/mp3')
                st.success("✅ Speech: Audio Generated")
            except: st.error("❌ Speech: gTTS not in requirements.txt")

            # D. CLOUD & ANALYTICS TEST
            st.write("Testing Database & Charts...")
            try:
                df_test = load_brain_data()
                st.bar_chart(pd.DataFrame({'test': [10, 20, 15]}), height=100)
                st.success(f"✅ Cloud & Charts: Connected ({len(df_test)} rows)")
            except: st.error("❌ Cloud/Charts: Failed")

            status.update(label="Diagnostics Complete!", state="complete", expanded=False)

    # 3. BRAIN BACKUP
    st.markdown("---")
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Brain Backup (.csv)",
            data=csv,
            file_name=f"BDL_Brain_Backup_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
        )

#--------------------
# SYSTEM DIAGNOSTIC TEST (ADMIN ONLY)
#--------------------
if st.session_state.is_admin:
    st.markdown("---")
    if st.sidebar.button("🛠️ Run System Stress Test"):
        with st.status("Running BDL Diagnostics...", expanded=True) as status:
            
            # 1. TEST: MATH ENGINE
            st.write("Testing Math Processor...")
            test_math = pd.eval("150 * 2 + 50")
            if test_math == 350:
                st.success("✅ Math: 350 (Passed)")
            
            # 2. TEST: HEBREW & RTL
            st.write("Testing Hebrew Translation...")
            try:
                from deep_translator import GoogleTranslator
                test_trans = GoogleTranslator(source='en', target='iw').translate("System Check")
                st.markdown(f'<div class="rtl-container">✅ Hebrew: {test_trans}</div>', unsafe_allow_html=True)
            except: st.error("❌ Hebrew: Failed")

            # 3. TEST: SPEECH ENGINE (TTS)
            st.write("Testing Speech Synth...")
            try:
                from gtts import gTTS
                import io
                tts = gTTS("System Online", lang='en')
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp, format='audio/mp3')
                st.success("✅ Speech: Audio Generated")
            except: st.error("❌ Speech: Library missing")

            # 4. TEST: CLOUD READING/SAVING
            st.write("Testing Cloud Sync...")
            try:
                df_test = load_brain_data()
                st.success(f"✅ Cloud: Connected ({len(df_test)} rows)")
            except: st.error("❌ Cloud: Disconnected")

            # 5. TEST: GRAPHING ENGINE
            st.write("Testing Analytics...")
            try:
                test_data = pd.DataFrame({'x': [1, 2, 3], 'y': [10, 20, 30]})
                st.bar_chart(test_data.set_index('x'))
                st.success("✅ Analytics: Rendered")
            except: st.error("❌ Analytics: Render Fail")

            status.update(label="All Systems Operational!", state="complete", expanded=False)

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


