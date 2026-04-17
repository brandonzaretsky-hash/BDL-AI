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
# Section 1: Setup & Session State
#--------------------
st.set_page_config(page_title="BDL.AI NEXUS", layout="wide", page_icon="🌐")

state_defaults = {
    "page": "Nexus Home",
    "messages": [],
    "has_run_splash": False,
    "dna_unlocked": False,
    "target_lang_code": "iw"
}
for key, value in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

#--------------------
# Section 2: Shared Core Engines (With Fixes)
#--------------------
conn = st.connection("gsheets", type=GSheetsConnection)

def get_total_intelligence():
    try:
        mem_df = conn.read(worksheet="Memory", ttl="1s")
        ctx_df = conn.read(worksheet="Context", ttl="1s")
        return len(mem_df) + len(ctx_df)
    except: return 0

def get_translation(text, target_lang):
    try: return GoogleTranslator(source='auto', target=target_lang).translate(text[:800])
    except: return None

def show_voices(e, t, lang_code):
    v1, v2 = st.columns(2)
    with v1:
        try:
            tts_e = gTTS(e[:3000], lang='en'); f_e = io.BytesIO(); tts_e.write_to_fp(f_e); st.audio(f_e)
        except: pass
    if t:
        with v2:
            try:
                tts_t = gTTS(t, lang=lang_code); f_t = io.BytesIO(); tts_t.write_to_fp(f_t); st.audio(f_t)
            except: pass

def run_deepthink_safe(q):
    """Deepthink engine with Disambiguation protection."""
    try:
        wikipedia.set_lang("en")
        search_results = wikipedia.search(q.strip())
        if not search_results:
            return "No data found in the global grid."
        
        try:
            # Try to get the first page
            page = wikipedia.page(search_results[0], auto_suggest=False)
            return page.summary
        except wikipedia.DisambiguationError as e:
            # If it's a 'choice' page, pick the first actual option
            first_option = e.options[0]
            page = wikipedia.page(first_option, auto_suggest=False)
            return f"*(Context: {first_option})*\n\n" + page.summary
        except wikipedia.PageError:
            return "Target located but the data stream is corrupted (Page Error)."
    except Exception as e:
        return f"Grid Scan Error: {str(e)}"

#--------------------
# Section 3: Visual Themes
#--------------------
def apply_theme(style_type):
    if style_type == "cyberpunk":
        st.markdown("""
            <style>
            .stApp { background-color: #000000; background-image: linear-gradient(180deg, #000000 0%, #051a05 100%); }
            section[data-testid="stSidebar"] { background-color: #051a05; border-right: 2px solid #00ff41; }
            h1, h2, h3, p, span, div { color: #00ff41 !important; font-family: 'Courier New', monospace; text-shadow: 0 0 8px #00ff41; }
            .stButton>button { background-color: #000; color: #00ff41; border: 1px solid #00ff41; box-shadow: 0 0 15px #00ff41; width: 100%; }
            .intel-counter { font-size: 60px; text-align: center; border: 2px solid #00ff41; padding: 20px; border-radius: 15px; box-shadow: inset 0 0 20px #00ff41; margin-bottom: 30px; }
            .stStatus { border: 1px solid #00ff41 !important; background: #000 !important; }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            .online-indicator { display: flex; align-items: center; justify-content: flex-end; color: #4CAF50; font-weight: bold; padding: 10px; }
            .dot { height: 10px; width: 10px; background-color: #4CAF50; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 8px #4CAF50; animation: pulse 2s infinite; }
            </style>
            """, unsafe_allow_html=True)

#--------------------
# PAGE: NEXUS HOME
#--------------------
def show_nexus_home():
    apply_theme("cyberpunk")
    st.markdown("<h1 style='text-align: center;'>BDL.AI NEXUS GATEWAY</h1>", unsafe_allow_html=True)
    
    intel_score = get_total_intelligence()
    st.markdown(f"<div class='intel-counter'>{intel_score}<br><span style='font-size: 20px;'>SYNTHESIZED LESSONS</span></div>", unsafe_allow_html=True)

    l_url = "https://lottie.host/8040d6c1-9031-4e76-9051-177b966b96e4/ZzQoUvV6wZ.json"
    r = requests.get(l_url); l_json = r.json() if r.status_code == 200 else None
    if l_json: st_lottie(l_json, height=250)

    st.markdown("<h3 style='text-align: center; margin-top: 20px;'>Select Bot Cortex:</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### 🤖 BDL")
        if st.button("INITIALIZE BDL"): st.session_state.page = "BDL Standard"; st.rerun()
    with c2:
        st.markdown("### 🧠 DEEPTHINK")
        if st.button("INITIALIZE DEEPTHINK"): st.session_state.page = "BDL Deepthink"; st.rerun()
    with c3:
        st.markdown("### 🧬 DNA")
        if st.button("INITIALIZE DNA"): st.session_state.page = "BDL DNA"; st.rerun()

#--------------------
# PAGE: BDL STANDARD
#--------------------
def show_bdl_standard():
    apply_theme("standard")
    if st.sidebar.button("⬅️ EXIT TO NEXUS"):
        st.session_state.page = "Nexus Home"; st.rerun()
    
    st.title("🤖 BDL Standard")
    
    with st.sidebar:
        st.markdown("### 🌍 Language Selection")
        lang_map = {"Hebrew": "iw", "French": "fr", "Spanish": "es", "German": "de", "Arabic": "ar", "Chinese": "zh-CN"}
        choice = st.selectbox("Language", list(lang_map.keys()))
        st.session_state.target_lang_code = lang_map[choice]
        voice_on = st.toggle("🔊 Voice", value=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Communicate..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        # Simple Q&A
        try:
            df = conn.read(worksheet="Memory", ttl="1s")
            qs = df['question'].fillna('').tolist()
            match, score = process.extractOne(prompt, qs, scorer=fuzz.token_sort_ratio)
            response = df[df['question'] == match].iloc[-1]['answer'] if score >= 85 else "I don't know that yet."
        except: response = "Memory offline."
        
        trans = get_translation(response, st.session_state.target_lang_code)
        full = f"{response}\n\n---\n**{choice}:** {trans}"
        with st.chat_message("assistant"):
            st.markdown(full)
            if voice_on: show_voices(response, trans, st.session_state.target_lang_code)
        st.session_state.messages.append({"role": "assistant", "content": full})

#--------------------
# PAGE: BDL DEEPTHINK (FIXED)
#--------------------
def show_bdl_deepthink():
    apply_theme("cyberpunk")
    if st.sidebar.button("⬅️ EXIT TO NEXUS"):
        st.session_state.page = "Nexus Home"; st.rerun()
    
    st.title("🧠 BDL Deepthink")
    
    prompt = st.chat_input("Scan Topic...")
    if prompt:
        with st.chat_message("user"): st.markdown(prompt)
        with st.status("📡 Searching Global Archives...", expanded=True) as s:
            res = run_deepthink_safe(prompt)
            s.update(label="Scan Complete", state="complete")
        
        with st.chat_message("assistant"):
            st.markdown(f"### 🔍 REPORT\n\n{res}")

#--------------------
# PAGE: BDL DNA
#--------------------
def show_bdl_dna():
    apply_theme("cyberpunk")
    if st.sidebar.button("⬅️ EXIT TO NEXUS"):
        st.session_state.page = "Nexus Home"; st.rerun()
    
    st.title("🧬 BDL DNA")
    
    if not st.session_state.dna_unlocked:
        st.error("🛑 Restricted Access")
        pw = st.text_input("Enter Passkey", type="password")
        if st.button("UNLOCK"):
            if pw == "qwerty":
                st.session_state.dna_unlocked = True; st.rerun()
            else: st.error("Access Denied")
    else:
        st.success("🟢 Lab Unlocked")
        st.info("DNA-Specific synthesis active.")

#--------------------
# ROUTER
#--------------------
if st.session_state.page == "Nexus Home": show_nexus_home()
elif st.session_state.page == "BDL Standard": show_bdl_standard()
elif st.session_state.page == "BDL Deepthink": show_bdl_deepthink()
elif st.session_state.page == "BDL DNA": show_bdl_dna()
