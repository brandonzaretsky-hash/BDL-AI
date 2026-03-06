import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fuzzywuzzy import fuzz, process
from deep_translator import GoogleTranslator
from gtts import gTTS
import io
import re
import wikipedia
import wikipediaapi
from datetime import datetime

# --- 1. INITIALIZATION & UI ---
st.set_page_config(page_title="BDL-ai V5.0", layout="wide", page_icon="🤖")

# Custom CSS for Right-to-Left Hebrew and UI Styling
st.markdown("""
    <style>
    .rtl-container { direction: rtl; text-align: right; font-family: 'Arial'; background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #444; }
    .stChatFloatingInputContainer { bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "waiting_for_answer" not in st.session_state:
    st.session_state.waiting_for_answer = False

# --- 2. SIDEBAR: TRIPLE-ROLE SECURITY (User, Admin, Speak) ---
with st.sidebar:
    st.title("🛡️ BDL Access Control")
    access_key = st.text_input("Enter Access Key", type="password")

    # ROLE DEFINITION
    # Super-User (Internet Brain): qwerty
    # Admin User (Sport/Graphs): admin
    # Standard User: [Any other or blank]
    is_speak_role = (access_key == "qwerty")
    is_admin_role = (access_key == "admin") or is_speak_role
    
    # --- LEVEL 1: USER TOOLS ---
    st.markdown("### 🛠️ Basic Controls")
    intel_level = st.slider("🧠 Intelligence Level", 50, 100, 85, help="Higher = stricter word matching.")
    hebrew_mode = st.toggle("🇮🇱 Hebrew Translation")
    voice_mode = st.toggle("🔊 Voice Response")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    # --- LEVEL 2: ADMIN TOOLS (qwerty or admin) ---
    if is_admin_role:
        st.markdown("---")
        st.markdown("### 👮 Admin Panel")
        sport_mode = st.toggle("🏒 Sport Mode", help="Summarizes NHL/Sports data automatically.")
        if st.button("📊 View Data Graph"):
            st.info("Neural mapping of Google Sheet data initiated...")
        if st.button("📋 Review Lessons"):
            st.info("No pending requests to verify.")

    # --- LEVEL 3: SPEAK TOOLS (qwerty Only) ---
    if is_speak_role:
        st.markdown("---")
        st.markdown("### ⚡ Super-User Tools")
        st.session_state.is_speak_mode = st.toggle("🌐 Internet Deep-Scan", value=True)
        st.success("SUPER-USER ACTIVE")
    else:
        st.session_state.is_speak_mode = False

# --- 3. DATA CONNECTION ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    def load_fresh_data():
        return conn.read(ttl="1s")
except Exception as e:
    st.error("Google Sheets Connection Error. Check your secrets configuration.")

# --- 4. CHAT INTERFACE ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# --- 5. LOGIC ENGINE ---
if prompt := st.chat_input("Communicate with BDL..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = ""
    hebrew_trans = ""

    # A. MATH ENGINE
    if re.match(r"^[\d\+\-\*\/\(\)\s\.]+$", prompt.strip()):
        try:
            response = f"🔢 **Calculation:** {pd.eval(prompt)}"
        except:
            pass

    # B. PRIMARY BRAIN
    if not response:
        current_df = load_fresh_data()
        
        # --- PATH 1: INTERNET BRAIN (Speak Role Only) ---
        if st.session_state.get('is_speak_mode'):
            import wikipediaapi
            from googlesearch import search
            wiki_link = wikipediaapi.Wikipedia('BDL-Bot/1.0', 'en')
            wikipedia.set_lang("en")
            
            # Summary vs Deep Scan logic
            wants_summary = "(summary)" in prompt.lower() or (is_admin_role and sport_mode)
            CHAR_LIMIT = 1200 if wants_summary else 15000 
            
            # Clean search query
            clean_q = prompt.lower().replace("(summary)", "")
            for noise in ['what is', 'who is', 'tell me about', '?']:
                clean_q = clean_q.replace(noise, "")
            
            with st.status("🚀 Global Knowledge Retrieval...", expanded=False) as status:
                try:
                    s_results = wikipedia.search(clean_q.strip())
                    if s_results:
                        page = wiki_link.page(s_results[0])
                        if page.exists():
                            # page.text for deep scan, page.summary for summary
                            content = page.summary if wants_summary else page.text
                            response = f"### 📂 DATA REPORT: {page.title}\n\n" + content[:CHAR_LIMIT]
                            if not wants_summary: response += "\n\n[--- END OF DEEP SCAN ---]"
                    
                    if not response:
                        res = list(search(prompt, num_results=1))
                        if res: response = f"Web Result: {res[0]}"
                except:
                    response = "Internet timeout. Brain is reconnecting..."
                status.update(label=f"Done: {len(response)} chars found", state="complete")

        # --- PATH 2: LOCAL MEMORY (User & Admin) ---
        if not response:
            # 1. Exact Match
            exact = current_df[current_df['question'].str.lower() == prompt.lower()]
            if not exact.empty:
                response = exact.iloc[-1]['answer']
            else:
                # 2. Fuzzy Match based on Slider
                questions = current_df['question'].fillna('').tolist()
                if questions:
                    match, score = process.extractOne(prompt, questions, scorer=fuzz.token_sort_ratio)
                    if score >= intel_level:
                        response = current_df[current_df['question'] == match].iloc[-1]['answer']

    # C. FALLBACK
    if not response:
        response = "I haven't learned that yet. **What is the answer?**"
        st.session_state.waiting_for_answer = True

    # D. TRANSLATION (Hebrew)
    if hebrew_mode and response and "Result:" not in response:
        try:
            hebrew_trans = GoogleTranslator(source='auto', target='iw').translate(response[:800])
        except:
            hebrew_trans = "Translation Error."

    # --- 6. VOICE & OUTPUT DISPLAY ---
    if response:
        full_display = response
        if hebrew_trans:
            full_display += f"\n\n---\n<div class='rtl-container'>🇮🇱 {hebrew_trans}</div>"
        
        with st.chat_message("assistant"):
            st.markdown(full_display, unsafe_allow_html=True)
            
            if voice_mode:
                v_col1, v_col2 = st.columns(2)
                with v_col1:
                    try:
                        tts_en = gTTS(response[:3000], lang='en')
                        f_en = io.BytesIO()
                        tts_en.write_to_fp(f_en)
                        st.audio(f_en, format='audio/mp3')
                        st.caption("🔊 English Audio")
                    except: st.warning("EN Voice Error")
                
                if hebrew_trans:
                    with v_col2:
                        try:
                            tts_he = gTTS(hebrew_trans, lang='iw')
                            f_he = io.BytesIO()
                            tts_he.write_to_fp(f_he)
                            st.audio(f_he, format='audio/mp3')
                            st.caption("🇮🇱 Hebrew Audio")
                        except: st.warning("HE Voice Error")
        
        st.session_state.messages.append({"role": "assistant", "content": full_display})
