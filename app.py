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
st.set_page_config(page_title="BDL.AI NEXUS", layout="wide", page_icon="🧠")

state_defaults = {
    "page": "Nexus Home",
    "messages": [],
    "has_run_splash": False,
    "dna_unlocked": False,
    "target_lang_code": "iw",
    "waiting_for_answer": False,
    "last_question": ""
}
for key, value in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

#--------------------
# Section 2: Visual Themes (Alignment Fixes Included)
#--------------------
def apply_theme(style_type):
    if style_type == "cyberpunk":
        st.markdown("""
            <style>
            .stApp {
                background-color: #000000;
                background-image: 
                    radial-gradient(circle at 50% 50%, rgba(255, 0, 255, 0.12) 0%, rgba(0, 0, 0, 1) 70%),
                    linear-gradient(180deg, #000 0%, #051a05 100%);
            }
            h1 { color: #FF00FF !important; text-shadow: 0 0 15px #FF00FF; text-align: center; font-weight: bold; margin-bottom: 0px !important; }
            h2, h3, .online-indicator { color: #00FFFF !important; text-shadow: 0 0 10px #00FFFF; text-align: center; }
            p, span, div, li { color: #00ff41 !important; font-family: 'Courier New', monospace; text-shadow: 0 0 5px #00ff41; }

            section[data-testid="stSidebar"] {
                background-color: #051a05;
                border-right: 2px solid #FF8C00; 
            }
            
            .stButton>button {
                background-color: #000; color: #00FFFF;
                border: 1px solid #00FFFF; box-shadow: 0 0 15px #00FFFF;
                width: 100%; height: 50px;
            }
            .stButton>button:hover {
                border: 1px solid #FF8C00; color: #FF8C00; box-shadow: 0 0 20px #FF8C00;
            }

            .intel-counter {
                font-size: 50px; text-align: center;
                border: 2px solid #00ff41; padding: 20px; border-radius: 15px;
                box-shadow: inset 0 0 30px rgba(0, 255, 65, 0.3), 0 0 20px rgba(0, 255, 65, 0.2);
                margin-bottom: 30px; background: rgba(0, 255, 65, 0.03);
            }
            
            /* ALIGNMENT CARD PROTOCOL */
            .bot-card {
                height: 250px; /* Forces all bot headers/icons to the same height */
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                margin-bottom: 10px;
            }

            .dev-box {
                position: relative; display: flex; flex-direction: column; 
                align-items: center; justify-content: center;
                background: transparent;
            }
            .caution-tape {
                position: absolute; top: 45px; left: -25px;
                width: 200px; height: 30px;
                background-color: #FF8C00; color: #000; font-weight: 1000;
                transform: rotate(-25deg); text-align: center; line-height: 30px;
                box-shadow: 0 0 20px #FF8C00; font-family: 'Impact', sans-serif;
                font-size: 16px; z-index: 10;
            }
            .online-indicator { font-weight: bold; text-align: right; margin-bottom: 10px; }
            .dot { height: 10px; width: 10px; background-color: #00FFFF; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 10px #00FFFF; }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            .online-indicator { display: flex; align-items: center; justify-content: flex-end; color: #4CAF50; font-weight: bold; padding: 10px; }
            .dot { height: 10px; width: 10px; background-color: #4CAF50; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 8px #4CAF50; animation: pulse 2s infinite; }
            @keyframes pulse { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }
            </style>
            """, unsafe_allow_html=True)

#--------------------
# Section 3: Shared Core Engines
#--------------------
conn = st.connection("gsheets", type=GSheetsConnection)

def get_total_intelligence():
    try:
        m = conn.read(worksheet="Memory", ttl="1s")
        c = conn.read(worksheet="Context", ttl="1s")
        return len(m) + len(c)
    except: return 0

def get_translation(text, target):
    try: return GoogleTranslator(source='auto', target=target).translate(text[:800])
    except: return None

def show_voices(e, t, code):
    v1, v2 = st.columns(2)
    with v1:
        try:
            tts_e = gTTS(e[:3000], lang='en'); f_e = io.BytesIO(); tts_e.write_to_fp(f_e); st.audio(f_e)
        except: pass
    if t:
        with v2:
            try:
                tts_t = gTTS(t, lang=code); f_t = io.BytesIO(); tts_t.write_to_fp(f_t); st.audio(f_t)
            except: pass

#--------------------
# PAGE: NEXUS HOME (Calibration Fix)
#--------------------
def show_nexus_home():
    apply_theme("cyberpunk")
    st.markdown("<h1>BDL.AI NEXUS GATEWAY</h1>", unsafe_allow_html=True)
    st.markdown("<div class='online-indicator'><span class='dot'></span>CORTEX ACTIVE</div>", unsafe_allow_html=True)
    
    score = get_total_intelligence()
    st.markdown(f"<div class='intel-counter'><span>{score}</span><br><span style='font-size: 16px;'>SYNTHESIZED LESSONS IN CORTEX</span></div>", unsafe_allow_html=True)

    l_url = "https://lottie.host/8040d6c1-9031-4e76-9051-177b966b96e4/ZzQoUvV6wZ.json"
    try:
        r = requests.get(l_url, timeout=5)
        if r.status_code == 200: st_lottie(r.json(), height=200, speed=1.2)
    except: pass

    st.markdown("<h3 style='margin-top: 20px;'>SELECT BOT MODULE TO ACTIVATE:</h3>", unsafe_allow_html=True)
    
    # Using fixed ratios to prevent horizontal shifting
    c1, c2, c3 = st.columns([1, 1, 1])
    
    with c1:
        st.markdown("""
            <div class='bot-card'>
                <img src='https://img.icons8.com/neon/120/bot.png' width='100'/>
                <h2 style='margin-top:10px;'>BDL</h2>
                <p>The original, but still great.</p>
            </div>
            """, unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE BDL"):
            st.session_state.page = "BDL Standard"; st.rerun()
            
    with c2:
        st.markdown("""
            <div class='bot-card'>
                <img src='https://img.icons8.com/neon/120/brain.png' width='100'/>
                <h2 style='margin-top:10px;'>DEEPTHINK</h2>
                <p>A web scanning powerhouse.</p>
            </div>
            """, unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE DEEPTHINK"):
            st.session_state.page = "BDL Deepthink"; st.rerun()
            
    with c3:
        st.markdown("""
            <div class='bot-card'>
                <div class='dev-box'>
                    <div class='caution-tape'>DEV-ONLY</div>
                    <div style='font-size: 80px;'>🧬</div>
                </div>
                <h2 style='margin-top:10px;'>DNA</h2>
                <p>An all-in-one cortex.</p>
            </div>
            """, unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE DNA"):
            st.session_state.page = "BDL DNA"; st.rerun()

#--------------------
# PAGE: BDL STANDARD
#--------------------
def show_bdl_standard():
    apply_theme("standard")
    if st.sidebar.button("⬅️ EXIT TO NEXUS"):
        st.session_state.page = "Nexus Home"; st.rerun()
    
    st.title("🤖 BDL Standard")
    
    with st.sidebar:
        st.markdown("### 🌍 Language Matrix")
        lang_map = {"Hebrew": "iw", "French": "fr", "Spanish": "es", "German": "de", "Arabic": "ar", "Chinese": "zh-CN", "Russian": "ru"}
        choice = st.selectbox("Select Language", list(lang_map.keys()))
        st.session_state.target_lang_code = lang_map[choice]
        voice_on = st.toggle("🔊 Speaking Mode", value=True)
        if st.button("🗑️ Clear Chat"): st.session_state.messages = []; st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Communicate..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        response = ""
        try:
            df = conn.read(worksheet="Memory", ttl="1s")
            qs = df['question'].fillna('').tolist()
            match, score = process.extractOne(prompt, qs, scorer=fuzz.token_sort_ratio)
            if score >= 85: response = df[df['question'] == match].iloc[-1]['answer']
        except: pass
        
        if not response: response = "I haven't learned that lesson yet."
        
        trans = get_translation(response, st.session_state.target_lang_code)
        full = f"{response}\n\n---\n**Translation:** {trans}"
        with st.chat_message("assistant"):
            st.markdown(full)
            if voice_on: show_voices(response, trans, st.session_state.target_lang_code)
        st.session_state.messages.append({"role": "assistant", "content": full})

#--------------------
# PAGE: DEEPTHINK
#--------------------
def show_bdl_deepthink():
    apply_theme("cyberpunk")
    if st.sidebar.button("⬅️ EXIT TO NEXUS"):
        st.session_state.page = "Nexus Home"; st.rerun()
    
    st.title("🧠 BDL Deepthink")
    prompt = st.chat_input("Scan Topic...")
    if prompt:
        with st.status("📡 Scanning Web Grid...", expanded=True):
            wikipedia.set_lang("en")
            search = wikipedia.search(prompt)
            res = wikipedia.page(search[0]).summary if search else "No data."
        st.markdown(f"### 🔍 SCAN RESULT\n\n{res}")

#--------------------
# PAGE: DNA
#--------------------
def show_bdl_dna():
    apply_theme("cyberpunk")
    if st.sidebar.button("⬅️ EXIT TO NEXUS"):
        st.session_state.page = "Nexus Home"; st.rerun()
    
    st.title("🧬 BDL DNA")
    if not st.session_state.dna_unlocked:
        st.error("🛑 ACCESS DENIED: Restricted Development Mode.")
        pw = st.text_input("ENTER PASSWORD", type="password")
        if st.button("UNLOCK"):
            if pw == "qwerty":
                st.session_state.dna_unlocked = True
                st.rerun()
            else: st.error("INCORRECT.")
    else:
        st.success("🟢 DNA UNLOCKED.")
        st.chat_input("DNA Synthesis Input...")

#--------------------
# ROUTER
#--------------------
if st.session_state.page == "Nexus Home":
    show_nexus_home()
elif st.session_state.page == "BDL Standard":
    show_bdl_standard()
elif st.session_state.page == "BDL Deepthink":
    show_bdl_deepthink()
elif st.session_state.page == "BDL DNA":
    show_bdl_dna()
