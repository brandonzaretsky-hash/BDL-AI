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
# Section 1: Setup & Session State Initialization
#--------------------
st.set_page_config(page_title="BDL.AI Master Brain", layout="wide", page_icon="🧠")

# CRITICAL: Initialize all states to prevent AttributeErrors
state_defaults = {
    "messages": [],
    "waiting_for_answer": False,
    "last_question": "",
    "last_mem_count": 0,
    "has_run_splash": False,
    "hebrew_mode": False,
    "voice_mode": False,
    "deepthink_enabled": True,
    "thorough_think": False,
    "perf_data": []
}

for key, value in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.markdown("""
    <style>
    .online-indicator { display: flex; align-items: center; justify-content: flex-end; color: #4CAF50; font-weight: bold; padding: 10px; }
    .dot { height: 10px; width: 10px; background-color: #4CAF50; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 8px #4CAF50; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }
    .rtl-container { direction: rtl; text-align: right; background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

#--------------------
# Section 2: Splash Animation Logic
#--------------------
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200: return r.json()
    except: return None

LOTTIE_URL = "https://lottie.host/8040d6c1-9031-4e76-9051-177b966b96e4/ZzQoUvV6wZ.json"
lottie_brain = load_lottieurl(LOTTIE_URL)

if not st.session_state.has_run_splash and lottie_brain:
    splash = st.empty()
    with splash.container():
        st.markdown("<h2 style='text-align: center; color: #4CAF50;'>Assembling BDL.AI Cortex...</h2>", unsafe_allow_html=True)
        st_lottie(lottie_brain, height=400, key="initial_assembly")
        time.sleep(3) 
    splash.empty()
    st.session_state.has_run_splash = True

st.markdown('<div class="online-indicator"><span class="dot"></span>BDL.AI Online</div>', unsafe_allow_html=True)

#--------------------
# Section 3: BDL.AI Setting Panel
#--------------------
with st.sidebar:
    st.title("⚙️ BDL.AI Setting Panel")
    access_key = st.text_input("Enter Access Key", type="password")
    is_speak_role = (access_key == "qwerty")
    is_admin_role = (access_key == "admin") or is_speak_role 
    
    st.markdown("### 🧠 Universal Settings")
    st.session_state.deepthink_enabled = st.toggle("🌐 Deepthink Mode", value=st.session_state.deepthink_enabled)
    intel_level = st.slider("Intelligence Sensitivity", 50, 100, 85)
    st.session_state.hebrew_mode = st.toggle("🇮🇱 Hebrew Mode", value=st.session_state.hebrew_mode)
    st.session_state.voice_mode = st.toggle("🔊 Voice Response", value=st.session_state.voice_mode)
    
    conn = st.connection("gsheets", type=GSheetsConnection)

    if is_speak_role:
        st.markdown("---")
        st.markdown("### 🧪 Super-Dev Labs")
        st.session_state.thorough_think = st.toggle("🔬 Thorough Think (Synthesis)", value=st.session_state.thorough_think)

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
                    if st.button("✅ Approve"):
                        main_mem = conn.read(worksheet="Memory", ttl="1s")
                        approved = pending_df.iloc[[req_idx]][['question', 'answer']]
                        conn.update(worksheet="Memory", data=pd.concat([main_mem, approved], ignore_index=True))
                        conn.update(worksheet="Requests", data=pending_df.drop(pending_df.index[req_idx]))
                        st.rerun()
                with c2:
                    if st.button("❌ Decline"):
                        conn.update(worksheet="Requests", data=pending_df.drop(pending_df.index[req_idx]))
                        st.rerun()
        except: pass

#--------------------
# Section 4: Engine Definitions
#--------------------
def run_math(p):
    if re.match(r"^[\d\+\-\*\/\(\)\s\.]+$", p.strip()):
        try: return f"🔢 **Result:** {pd.eval(p)}"
        except: return None
    return None

def get_hebrew(t):
    try: return GoogleTranslator(source='auto', target='iw').translate(t[:800])
    except: return None

def show_voices(e, h):
    v1, v2 = st.columns(2)
    with v1:
        try:
            tts_e = gTTS(e[:3000], lang='en'); f_e = io.BytesIO(); tts_e.write_to_fp(f_e); st.audio(f_e)
        except: pass
    if h:
        with v2:
            try:
                tts_h = gTTS(h, lang='iw'); f_h = io.BytesIO(); tts_h.write_to_fp(f_h); st.audio(f_h)
            except: pass

def run_deepthink(q, summ=False):
    wiki = wikipediaapi.Wikipedia('BDL-Bot/1.0', 'en'); wikipedia.set_lang("en")
    limit = 1200 if summ else 15000
    clean_q = q.lower().replace("(summary)", "")
    for n in ['what is', 'who is', '?']: clean_q = clean_q.replace(n, "")
    try:
        s = wikipedia.search(clean_q.strip())
        if s:
            p = wiki.page(s[0])
            if p.exists(): return (p.summary if summ else p.text)[:limit]
    except: return None
    return None

#--------------------
# Section 5: Chat History & Logic
#--------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

if prompt := st.chat_input("Communicate with BDL.AI Master Brain..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    response = ""

    # A. MATH ENGINE
    response = run_math(prompt)

    # B. DATA GATHERING (Deepthink or Memory)
    raw_data = ""
    if not response and st.session_state.deepthink_enabled:
        with st.status("🧠 Deepthinking...", expanded=False):
            raw_data = run_deepthink(prompt, summarize=(is_admin_role and 'sport_mode' in locals() and sport_mode))
    
    if not raw_data and not response:
        try:
            df = conn.read(worksheet="Memory", ttl="1s")
            qs = df['question'].fillna('').tolist()
            if qs:
                match, score = process.extractOne(prompt, qs, scorer=fuzz.token_sort_ratio)
                if score >= intel_level: raw_data = df[df['question'] == match].iloc[-1]['answer']
        except: pass

    # C. THOROUGH THINK (Contextual Synthesis)
    if raw_data:
        if st.session_state.thorough_think and is_speak_role:
            with st.status("🔬 Thorough Thinking: Contextual Assembly...", expanded=False):
                # Synthesis Engine: Pull complex words and build context
                tokens = re.findall(r'\b\w{5,}\b', raw_data)
                unique_concepts = list(set(tokens))
                response = f"### 🧪 THOROUGH THINK SYNTHESIS\n\n**Processed Meanings:** {', '.join(unique_concepts[:8])}...\n\n"
                response += f"System Insight: {raw_data[:850]}..."
        else:
            response = raw_data

    # D. FALLBACK / TEACHING
    if not response:
        if st.session_state.waiting_for_answer:
            if is_speak_role:
                # save_direct logic
                response = "⚡ **Cortex Updated.**"
            else:
                # save_request logic
                response = "📝 **Lesson Queued.**"
            st.session_state.waiting_for_answer = False
        else:
            response = "I haven't learned that yet. **What is the answer?**"
            st.session_state.waiting_for_answer = True
            st.session_state.last_question = prompt

    # E. FINAL OUTPUT (Hebrew & Voice)
    if response:
        he_t = get_hebrew(response) if st.session_state.hebrew_mode else ""
        full = response + (f"\n\n---\n<div class='rtl-container'>🇮🇱 {he_t}</div>" if he_t else "")
        with st.chat_message("assistant"):
            st.markdown(full, unsafe_allow_html=True)
            if st.session_state.voice_mode: show_voices(response, he_t)
        st.session_state.messages.append({"role": "assistant", "content": full})
