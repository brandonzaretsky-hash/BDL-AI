import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fuzzywuzzy import fuzz, process
from deep_translator import GoogleTranslator
from gtts import gTTS
from streamlit_lottie import st_lottie
import io, re, wikipedia, wikipediaapi, time, requests, random
from datetime import datetime

#--------------------
# Section 0: Splash Animation (Stable)
#--------------------
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200: return None
        return r.json()
    except: return None

LOTTIE_URL = "https://lottie.host/8040d6c1-9031-4e76-9051-177b966b96e4/ZzQoUvV6wZ.json"
lottie_brain = load_lottieurl(LOTTIE_URL)

if "has_run_splash" not in st.session_state: st.session_state.has_run_splash = False

def run_brain_assembly():
    if not st.session_state.has_run_splash and lottie_brain:
        splash_container = st.empty()
        with splash_container.container():
            st.markdown("<h2 style='text-align: center; color: #4CAF50;'>Assembling BDL.AI Cortex...</h2>", unsafe_allow_html=True)
            st_lottie(lottie_brain, height=400, key="initial_assembly")
            time.sleep(3) 
        splash_container.empty()
        st.session_state.has_run_splash = True

#--------------------
# Section 1: Setup & Indicator
#--------------------
st.set_page_config(page_title="BDL.AI Master Brain", layout="wide", page_icon="🧠")
st.markdown("""
    <style>
    .online-indicator { display: flex; align-items: center; justify-content: flex-end; color: #4CAF50; font-weight: bold; padding: 10px; }
    .dot { height: 10px; width: 10px; background-color: #4CAF50; border-radius: 50%; display: inline-block; margin-right: 8px; box-shadow: 0 0 8px #4CAF50; animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 0.4; } 50% { opacity: 1; } 100% { opacity: 0.4; } }
    .rtl-container { direction: rtl; text-align: right; background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

run_brain_assembly()
st.markdown('<div class="online-indicator"><span class="dot"></span>BDL.AI Online</div>', unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "waiting_for_answer" not in st.session_state: st.session_state.waiting_for_answer = False
if "last_question" not in st.session_state: st.session_state.last_question = ""
if "last_mem_count" not in st.session_state: st.session_state.last_mem_count = 0

#--------------------
# Section 2: BDL.AI Setting Panel
#--------------------
with st.sidebar:
    st.title("⚙️ BDL.AI Setting Panel")
    access_key = st.text_input("Enter Access Key", type="password")
    is_speak_role = (access_key == "qwerty")
    is_admin_role = (access_key == "admin") or is_speak_role 
    
    st.markdown("### 🧠 Universal Settings")
    st.session_state.deepthink_enabled = st.toggle("🌐 Deepthink Mode (Internet)", value=True)
    intel_level = st.slider("Intelligence Sensitivity", 50, 100, 85)
    hebrew_mode = st.toggle("🇮🇱 Hebrew Mode")
    voice_mode = st.toggle("🔊 Voice Response")
    
    conn = st.connection("gsheets", type=GSheetsConnection)

    # THOROUGH THINK MODE: SUPER-DEV ONLY
    if is_speak_role:
        st.markdown("---")
        st.markdown("### 🧪 Super-Dev Labs")
        st.session_state.thorough_think = st.toggle("🔬 Thorough Think (Contextual Synthesis)", value=False)

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
                        st.session_state.has_run_splash = False 
                        st.rerun()
                with c2:
                    if st.button("❌ Decline"):
                        conn.update(worksheet="Requests", data=pending_df.drop(pending_df.index[req_idx]))
                        st.rerun()
        except: pass

#--------------------
# Section 11: Logic - Sports, Deepthink, and Thorough Think
#--------------------
if prompt := st.chat_input("Communicate..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    response = ""

    # A. TEACHING
    if st.session_state.waiting_for_answer:
        if is_speak_role:
            save_direct(st.session_state.last_question, prompt)
            response = "⚡ **Cortex Updated.**"
        else:
            save_request(st.session_state.last_question, prompt)
            response = "📝 **Lesson Queued.**"
        st.session_state.waiting_for_answer = False

    # B. MATH
    if not response: response = run_math(prompt)

    # C. DATA ACQUISITION (Deepthink or Memory)
    source_text = ""
    if not response and st.session_state.deepthink_enabled:
        with st.status("🧠 Deepthinking...", expanded=False):
            source_text = run_deepthink(prompt, summarize=(is_admin_role and sport_mode))
    
    if not source_text and not response:
        source_text = read_local_memory(prompt, intel_level)

    # D. THOROUGH THINK PROCESSING (Super-Dev Only)
    if source_text and st.session_state.get('thorough_think') and is_speak_role:
        with st.status("🔬 Thorough Thinking: Assembling Context...", expanded=False):
            # 1. Pull all words and context
            words = re.findall(r'\b\w{4,}\b', source_text) # Extract meaningful words
            unique_words = list(set(words))
            
            # 2. Simulate sentence assembly based on prompt keywords
            context_highlights = [w for w in unique_words if any(p_word in w.lower() for p_word in prompt.lower().split())]
            
            # 3. Assemble Custom Response
            response = f"### 🧪 THOROUGH THINK SYNTHESIS\n\n"
            response += f"**Analyzed Context:** {', '.join(context_highlights[:5])}...\n\n"
            # Rebuilding a core meaning sentence
            response += f"Based on the processed words, the system has assembled this insight: "
            response += f"{source_text[:500]}..." # Still provides the data but marked as synthesized
    else:
        response = source_text

    # E. FALLBACK
    if not response:
        response = "I haven't learned that yet. **What is the answer?**"
        st.session_state.waiting_for_answer = True
        st.session_state.last_question = prompt

    # F. OUTPUT
    if response:
        he_t = get_hebrew(response) if st.session_state.get('hebrew_mode') else ""
        full = response + (f"\n\n---\n<div class='rtl-container'>🇮🇱 {he_t}</div>" if he_t else "")
        with st.chat_message("assistant"):
            st.markdown(full, unsafe_allow_html=True)
            if st.session_state.get('voice_mode'): show_voices(response, he_t)
        st.session_state.messages.append({"role": "assistant", "content": full})
