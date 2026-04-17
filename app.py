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
# Section 1: Setup & Routing Defaults
#--------------------
st.set_page_config(page_title="BDL.AI NEXUS", layout="wide", page_icon="🧠")

# Initialize global states
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
# Section 2: Visual Themes (Standard vs. NEXUS Cyberpunk)
#--------------------
def apply_theme(style_type):
    if style_type == "cyberpunk":
        # REDESIGN: Multicolored Neon Cyberpunk
        st.markdown("""
            <style>
            .stApp {
                background-color: #000000;
                /* Neon brain pulse effect background */
                background-image: 
                    radial-gradient(circle at 50% 50%, rgba(255, 0, 255, 0.08) 0%, rgba(0, 0, 0, 1) 60%),
                    linear-gradient(180deg, #000 0%, #051a05 100%);
            }
            
            /* GLOBAL TEXT PROTOCOLS */
            h1 { color: #FF00FF !important; text-shadow: 0 0 10px #FF00FF; } /* Neon Pink Titles */
            h2, h3, .online-indicator { color: #00FFFF !important; text-shadow: 0 0 10px #00FFFF; } /* Neon Blue Subtitles */
            p, span, div, li { color: #00ff41 !important; font-family: 'Courier New', monospace; text-shadow: 0 0 5px #00ff41; } /* Classic Green Body */

            section[data-testid="stSidebar"] {
                background-color: #051a05;
                border-right: 2px solid #FF8C00; /* Naomi Orange Accent Border */
            }
            
            /* NEON ORANGE ELEMENTS (Naomi Orange) */
            .stSlider>div>div>div>div, .stButton>button:hover {
                background-color: #FF8C00 !important; color: #000 !important;
            }

            /* NEON BLUE ELEMENTS (Cyan) */
            .stButton>button {
                background-color: #000; color: #00FFFF;
                border: 1px solid #00FFFF; box-shadow: 0 0 15px #00FFFF;
            }

            /* INTEL COUNTER PROTOCOL */
            .intel-counter {
                font-size: 50px; text-align: center;
                border: 2px solid #00ff41; padding: 20px; border-radius: 15px;
                box-shadow: inset 0 0 30px rgba(0, 255, 65, 0.3), 0 0 20px rgba(0, 255, 65, 0.2);
                margin-bottom: 30px;
                background: rgba(0, 255, 65, 0.03);
            }
            .intel-counter span { color: #00ff41 !important; text-shadow: 0 0 8px #00ff41; }
            
            /* CAUTION TAPE PROTOCOL */
            .dev-box {
                position: relative;
                display: flex; flex-direction: column; align-items: center; justify-content: center;
                border: 2px solid #FFD700;
                padding: 10px; border-radius: 10px;
                overflow: hidden;
            }
            .caution-tape {
                position: absolute; top: 30px; left: -20px;
                width: 150px; height: 25px;
                background-color: #FFD700; color: #000; font-weight: bold;
                transform: rotate(-35deg); text-align: center; line-height: 25px;
                box-shadow: 0 0 10px #FFD700;
                font-family: Arial, sans-serif;
            }
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
# Section 3: Core Shared Engines (Memory / Voice / Translation)
#--------------------
conn = st.connection("gsheets", type=GSheetsConnection)

def get_total_intelligence():
    """Calculates total lessons + context blocks learned."""
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

def run_deepthink_summ(q):
    """Wikipedia summary lookup for Deepthink standard mode"""
    wikipedia.set_lang("en")
    try:
        search = wikipedia.search(q.strip())
        if search:
            return wikipedia.page(search[0]).summary
    except: return None
    return None

#--------------------
# PAGE: NEXUS HOME (Gateway)
#--------------------
def show_nexus_home():
    apply_theme("cyberpunk")
    st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>BDL.AI NEXUS GATEWAY</h1>", unsafe_allow_html=True)
    st.markdown("<div class='online-indicator'><span class="dot"></span>CORTEX ACTIVE</div>", unsafe_allow_html=True)
    
    # Intelligence Counter Protocol
    intel_score = get_total_intelligence()
    st.markdown(f"<div class='intel-counter'><span>{intel_score}</span><br><span style='font-size: 16px;'>SYNTHESIZED LESSONS IN CORTEX</span></div>", unsafe_allow_html=True)

    # Pulsing Brain Animation (Cyberpunk vibe)
    l_url = "https://lottie.host/8040d6c1-9031-4e76-9051-177b966b96e4/ZzQoUvV6wZ.json"
    r = requests.get(l_url); l_json = r.json() if r.status_code == 200 else None
    if l_json: st_lottie(l_json, height=220, speed=1.2)

    st.markdown("<h3 style='text-align: center; margin-top: 20px; color:#00FFFF !important;'>SELECT BOT MODULE TO ACTIVATE:</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    
    # BOT 1: BDL STANDARD
    with c1:
        st.markdown("<div align='center'><img src='https://img.icons8.com/neon/120/bot.png' style='margin-bottom:15px;'/></div>", unsafe_allow_html=True)
        st.markdown("## BDL")
        st.caption("The original, but still great.")
        if st.button("🔌 INITIALIZE BDL CORTEX"):
            st.session_state.page = "BDL Standard"; st.rerun()
            
    # BOT 2: DEEPTHINK
    with c2:
        st.markdown("<div align='center'><img src='https://img.icons8.com/neon/120/brain.png' style='margin-bottom:15px;'/></div>", unsafe_allow_html=True)
        st.markdown("## DEEPTHINK")
        st.caption("A web scanning powerhouse.")
        if st.button("🔌 INITIALIZE DEEPTHINK CORTEX"):
            st.session_state.page = "BDL Deepthink"; st.rerun()
            
    # BOT 3: DNA (Under Development)
    with c3:
        # Caution Tape Overlay Protocol
        st.markdown("""
            <div class='dev-box'>
                <div class='caution-tape'>DEV-MODE</div>
                <img src='https://img.icons8.com/neon/120/dna.png' style='margin-bottom:15px;'/>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("## DNA")
        st.caption("An all-in-one cortex.")
        if st.button("🔌 INITIALIZE DNA CORTEX"):
            st.session_state.page = "BDL DNA"; st.rerun()

#--------------------
# PAGE: BDL STANDARD (Normal Vibe)
#--------------------
def show_bdl_standard():
    apply_theme("standard")
    if st.sidebar.button("⬅️ EXIT TO NEXUS"):
        st.session_state.page = "Nexus Home"; st.rerun()
    
    st.title("🤖 BDL Standard")
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🌐 Universal Language Matrix")
        # Global Language Engine
        lang_map = {
            "Hebrew": "iw", "French": "fr", "Spanish": "es", "German": "de", "Italian": "it", 
            "Arabic": "ar", "Chinese": "zh-CN", "Japanese": "ja", "Russian": "ru", "Portuguese": "pt",
            "Hindi": "hi", "Dutch": "nl", "Greek": "el", "Turkish": "tr", "Korean": "ko"
        }
        choice = st.selectbox("Select Target Language", list(lang_map.keys()))
        st.session_state.target_lang_code = lang_map[choice]
        voice_on = st.toggle("🔊 Speaking Mode", value=True)
        intel_level = st.slider("Cortex Sensitivity", 50, 100, 85)
        if st.button("🗑️ Reset Cortex History"): st.session_state.messages = []; st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Ask BDL..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        response = ""
        try:
            df = conn.read(worksheet="Memory", ttl="1s")
            qs = df['question'].fillna('').tolist()
            match, score = process.extractOne(prompt, qs, scorer=fuzz.token_sort_ratio)
            if score >= intel_level: response = df[df['question'] == match].iloc[-1]['answer']
        except: pass
        
        if not response: response = "I haven't been taught that specific lesson yet."
        
        # Translation Engine
        trans = get_translation(response, st.session_state.target_lang_code)
        full = f"{response}\n\n---\n**Translation ({choice}):** {trans}"
        
        with st.chat_message("assistant"):
            st.markdown(full)
            if voice_on: show_voices(response, trans, st.session_state.target_lang_code)
        st.session_state.messages.append({"role": "assistant", "content": full})

#--------------------
# PAGE: BDL DEEPTHINK (Cyberpunk Vibe)
#--------------------
def show_bdl_deepthink():
    apply_theme("cyberpunk")
    if st.sidebar.button("⬅️ EXIT TO NEXUS"):
        st.session_state.page = "Nexus Home"; st.rerun()
    
    st.title("🧠 BDL Deepthink")
    st.caption("WEB SCANNING POWERHOUSE ACTIVE.")
    
    prompt = st.chat_input("Enter Topic for Global Web Scan...")
    if prompt:
        with st.chat_message("user"): st.markdown(prompt)
        with st.status("📡 Rerouting through Wikipedia Grid...", expanded=True):
            res = run_deepthink_summ(prompt)
            if not res: res = "No data found in the global grid."
        
        with st.chat_message("assistant"):
            st.markdown(f"### 🔍 DEEP SCAN RESULT\n\n{res}")

#--------------------
# PAGE: BDL DNA (Cyberpunk Vibe + Lock)
#--------------------
def show_bdl_dna():
    apply_theme("cyberpunk")
    if st.sidebar.button("⬅️ EXIT TO NEXUS"):
        st.session_state.page = "Nexus Home"; st.rerun()
    
    st.title("🧬 BDL DNA")
    st.caption("ALL-IN-ONE CORTEX MODE ACTIVE.")
    
    if not st.session_state.dna_unlocked:
        st.error("🛑 ACCESS DENIED: BDL DNA is currently in restricted development mode.")
        pw = st.text_input("ENTER SUPER-DEV OVERRIDE CODE", type="password")
        if st.button("AUTHORIZE"):
            if pw == "qwerty":
                st.session_state.dna_unlocked = True
                st.rerun()
            else: st.error("CODE INCORRECT.")
    else:
        st.success("🟢 ACCESS GRANTED. Thorough Think Synthesis Active.")
        st.info("The Context Bank and Synthesis Engines will activate on your next update.")
        # Thorough Think / Cortex Training logic goes here later.

#--------------------
# THE NEXUS ROUTER PROTOCOL
#--------------------
if st.session_state.page == "Nexus Home":
    show_nexus_home()
elif st.session_state.page == "BDL Standard":
    show_bdl_standard()
elif st.session_state.page == "BDL Deepthink":
    show_bdl_deepthink()
elif st.session_state.page == "BDL DNA":
    show_bdl_dna()
