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
# Section 0: Splash Animation & Update Logic
#--------------------
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200: return None
    return r.json()

# Lottie for Robotic Assembly/AI Brain
lottie_brain = load_lottieurl("https://lottie.host/8040d6c1-9031-4e76-9051-177b966b96e4/ZzQoUvV6wZ.json")

# Initialize Session States
if "messages" not in st.session_state: st.session_state.messages = []
if "waiting_for_answer" not in st.session_state: st.session_state.waiting_for_answer = False
if "last_question" not in st.session_state: st.session_state.last_question = ""
if "perf_data" not in st.session_state: st.session_state.perf_data = []
if "last_mem_count" not in st.session_state: st.session_state.last_mem_count = 0
if "has_run_splash" not in st.session_state: st.session_state.has_run_splash = False

#--------------------
# Section 1: Setup & CSS (The Online Indicator)
#--------------------
st.set_page_config(page_title="BDL-ai V6.5 Master", layout="wide", page_icon="🧠")

st.markdown("""
    <style>
    /* BDL.AI Online Indicator */
    .online-indicator {
        display: flex; align-items: center; justify-content: flex-end;
        padding: 10px; font-weight: bold; color: #4CAF50;
    }
    .dot {
        height: 10px; width: 10px; background-color: #4CAF50;
        border-radius: 50%; display: inline-block; margin-right: 8px;
        box-shadow: 0 0 8px #4CAF50; animation: pulse-green 2s infinite;
    }
    @keyframes pulse-green {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
    }
    .rtl-container { direction: rtl; text-align: right; background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #444; }
    </style>
    """, unsafe_allow_html=True)

#--------------------
# Section 2: Sidebar (BDL.AI Setting Panel)
#--------------------
with st.sidebar:
    st.title("⚙️ BDL.AI Setting Panel")
    access_key = st.text_input("Enter Access Key", type="password")

    is_speak_role = (access_key == "qwerty")
    is_admin_role = (access_key == "admin") or is_speak_role 
    
    st.markdown("### 🧠 Universal Brain Settings")
    st.session_state.deepthink_enabled = st.toggle("🌐 Deepthink Mode (Internet)", value=False)
    intel_level = st.slider("Intelligence Sensitivity", 50, 100, 85)
    hebrew_mode = st.toggle("🇮🇱 Hebrew Mode")
    voice_mode = st.toggle("🔊 Voice Response")
    
    conn = st.connection("gsheets", type=GSheetsConnection)

    if is_admin_role:
        st.markdown("---")
        st.markdown("### 👮 Admin Control Center")
        sport_mode = st.toggle("🏒 Sport Mode")
        
        try:
            pending_df = conn.read(worksheet="Requests", ttl="1s")
            if not pending_df.empty:
                st.dataframe(pending_df, use_container_width=True)
                req_idx = st.number_input("ID to Manage", 0, len(pending_df)-1, 0)
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Approve Lesson"):
                        main_mem = conn.read(worksheet="Memory", ttl="1s")
                        approved = pending_df.iloc[[req_idx]][['question', 'answer']]
                        conn.update(worksheet="Memory", data=pd.concat([main_mem, approved], ignore_index=True))
                        conn.update(worksheet="Requests", data=pending_df.drop(pending_df.index[req_idx]))
                        st.session_state.has_run_splash = False # Force Splash on update
                        st.rerun()
                with c2:
                    if st.button("❌ Decline Lesson"):
                        conn.update(worksheet="Requests", data=pending_df.drop(pending_df.index[req_idx]))
                        st.rerun()
        except: pass

    if st.button("🗑️ Reset Cortex"):
        st.session_state.messages = []
        st.rerun()

#--------------------
# Section 3: Brain Assembly Animation & Top Indicator
#--------------------
header_col1, header_col2 = st.columns([8, 2])
with header_col2:
    st.markdown('<div class="online-indicator"><span class="dot"></span>BDL.AI Online</div>', unsafe_allow_html=True)

# Detect if we need to show the Assembly Animation
try:
    current_mem = conn.read(worksheet="Memory", ttl="1s")
    current_count = len(current_mem)
    if st.session_state.last_mem_count == 0: st.session_state.last_mem_count = current_count
    
    update_detected = current_count > st.session_state.last_mem_count
    
    if not st.session_state.has_run_splash or update_detected:
        splash_container = st.empty()
        with splash_container.container():
            st.markdown("<h2 style='text-align: center; color: #4CAF50;'>Assembling BDL.AI Cortex...</h2>", unsafe_allow_html=True)
            st_lottie(lottie_brain, height=400, key="splash")
            time.sleep(2.5) # Time for "Robotic Assembly"
            st.toast("Brain Pulse Green... System Initialized.")
            time.sleep(1)
        splash_container.empty()
        st.session_state.has_run_splash = True
        st.session_state.last_mem_count = current_count
        if update_detected: st.success("🔔 **Global Update:** New knowledge has been integrated into the cortex!")
except: pass

#--------------------
# Section 4: Data Logic & Chat History
#--------------------
def save_direct(q, a):
    df = conn.read(worksheet="Memory", ttl="1s")
    new_row = pd.DataFrame([{"question": q.lower(), "answer": a}])
    conn.update(worksheet="Memory", data=pd.concat([df, new_row], ignore_index=True))

def save_request(q, a):
    df = conn.read(worksheet="Requests", ttl="1s")
    new_req = pd.DataFrame([{"question": q.lower(), "answer": a, "user": "User", "timestamp": datetime.now().strftime("%H:%M")}])
    conn.update(worksheet="Requests", data=pd.concat([df, new_req], ignore_index=True))

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

#--------------------
# Section 5-10: Support Engines (Math, Translation, Voice, Deepthink)
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
            if p.exists(): return f"### 🧠 DEEPTHINK REPORT: {p.title}\n\n" + (p.summary if summ else p.text)[:limit]
    except: return None
    return None

#--------------------
# Section 11: Main Brain Logic
#--------------------
if prompt := st.chat_input("Communicate with BDL.AI Master Brain..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    response = ""
    he_t = ""

    if st.session_state.waiting_for_answer:
        if is_speak_role:
            save_direct(st.session_state.last_question, prompt)
            response = "⚡ **System Core Updated.** Knowledge added."
        else:
            save_request(st.session_state.last_question, prompt)
            response = "📝 **Lesson Queued.** Waiting for Admin approval."
        st.session_state.waiting_for_answer = False

    if not response: response = run_math(prompt)

    if not response and st.session_state.deepthink_enabled:
        start = time.time()
        with st.status("🧠 Deepthinking...", expanded=False) as s:
            response = run_deepthink(prompt, summarize=("(summary)" in prompt.lower() or (is_admin_role and sport_mode)))
            s.update(label="Deepthink Scan Complete!", state="complete")
        st.session_state.perf_data.append(time.time() - start)

    if not response:
        try:
            df = conn.read(worksheet="Memory", ttl="1s")
            qs = df['question'].fillna('').tolist()
            if qs:
                match, score = process.extractOne(prompt, qs, scorer=fuzz.token_sort_ratio)
                if score >= intel_level: response = df[df['question'] == match].iloc[-1]['answer']
        except: pass

    if not response:
        response = "I haven't learned that yet. **What is the answer?**"
        st.session_state.waiting_for_answer = True
        st.session_state.last_question = prompt

    if response:
        if hebrew_mode and "Result:" not in response: he_t = get_hebrew(response)
        full = response + (f"\n\n---\n<div class='rtl-container'>🇮🇱 {he_t}</div>" if he_t else "")
        with st.chat_message("assistant"):
            st.markdown(full, unsafe_allow_html=True)
            if voice_mode: show_voices(response, he_t)
        st.session_state.messages.append({"role": "assistant", "content": full})

#--------------------
# Section 12: Diagnostics
#--------------------
if is_speak_role:
    with st.sidebar:
        st.markdown("---")
        if st.button("🧪 Diagnostics"):
            st.write(f"Perf Graph: {len(st.session_state.perf_data)} scans logged.")
