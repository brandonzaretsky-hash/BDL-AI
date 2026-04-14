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
st.set_page_config(page_title="BDL.AI Master Brain", layout="wide", page_icon="🧠")

state_defaults = {
    "messages": [],
    "waiting_for_answer": False,
    "last_question": "",
    "last_mem_count": 0,
    "has_run_splash": False,
    "hebrew_mode": False,
    "voice_mode": False,
    "deepthink_enabled": True,
    "thorough_think": False
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
# Section 2: Splash Animation
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
# Section 3: Data Functions
#--------------------
def save_direct(q, a, conn):
    df = conn.read(worksheet="Memory", ttl="1s")
    new_row = pd.DataFrame([{"question": q.lower(), "answer": a}])
    conn.update(worksheet="Memory", data=pd.concat([df, new_row], ignore_index=True))

def save_request(q, a, conn):
    df = conn.read(worksheet="Requests", ttl="1s")
    new_req = pd.DataFrame([{"question": q.lower(), "answer": a, "user": "User", "timestamp": datetime.now().strftime("%H:%M")}])
    conn.update(worksheet="Requests", data=pd.concat([df, new_req], ignore_index=True))

def save_context_request(topic, meaning, conn):
    """Saves to the PENDING ContextRequests tab for everyone"""
    df = conn.read(worksheet="ContextRequests", ttl="1s")
    new_req = pd.DataFrame([{
        "Topic": topic.lower(),
        "Meaning": meaning,
        "User": "External",
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }])
    conn.update(worksheet="ContextRequests", data=pd.concat([df, new_req], ignore_index=True))

#--------------------
# Section 4: Engine Definitions (Math, Voice, Deepthink, etc.)
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
# Section 5: BDL.AI Setting Panel
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

    # --- UNIVERSAL TRAINING (For All Users) ---
    st.markdown("---")
    with st.expander("📚 Train BDL Cortex"):
        st.caption("Suggest raw knowledge blocks for the synthesis engine.")
        u_topic = st.text_input("Topic Name", key="utopic")
        u_meaning = st.text_area("Detailed Meaning (Paragraph)", key="umeaning")
        if st.button("Submit for Review"):
            if u_topic and u_meaning:
                save_context_request(u_topic, u_meaning, conn)
                st.info("Sent to Super-Dev for assembly.")

    # --- SUPER-DEV VAULT (Approval Panel) ---
    if is_speak_role:
        st.markdown("---")
        st.markdown("### 🧪 Super-Dev Vault")
        st.session_state.thorough_think = st.toggle("🔬 Thorough Think", value=st.session_state.thorough_think)
        
        try:
            # Context Approval
            c_pending = conn.read(worksheet="ContextRequests", ttl="1s")
            if not c_pending.empty:
                st.markdown("**Pending Context Blocks:**")
                st.dataframe(c_pending, use_container_width=True)
                c_idx = st.number_input("Context ID", 0, len(c_pending)-1, 0)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Approve Context"):
                        main_context = conn.read(worksheet="Context", ttl="1s")
                        approved_c = c_pending.iloc[[c_idx]][['Topic', 'Meaning']]
                        conn.update(worksheet="Context", data=pd.concat([main_context, approved_c], ignore_index=True))
                        conn.update(worksheet="ContextRequests", data=c_pending.drop(c_pending.index[c_idx]))
                        st.rerun()
                with col2:
                    if st.button("❌ Decline Context"):
                        conn.update(worksheet="ContextRequests", data=c_pending.drop(c_pending.index[c_idx]))
                        st.rerun()
        except: pass

    # Admin Control (Existing Q&A Approval)
    if is_admin_role:
        st.markdown("---")
        st.markdown("### 👮 Admin Controls")
        sport_mode = st.toggle("🏒 Sport Mode")
        try:
            pending_df = conn.read(worksheet="Requests", ttl="1s")
            if not pending_df.empty:
                st.dataframe(pending_df, use_container_width=True)
                req_idx = st.number_input("Request ID", 0, len(pending_df)-1, 0)
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("✅ Approve Lesson"):
                        main_m = conn.read(worksheet="Memory", ttl="1s")
                        app_row = pending_df.iloc[[req_idx]][['question', 'answer']]
                        conn.update(worksheet="Memory", data=pd.concat([main_m, app_row], ignore_index=True))
                        conn.update(worksheet="Requests", data=pending_df.drop(pending_df.index[req_idx]))
                        st.rerun()
                with b2:
                    if st.button("❌ Decline Lesson"):
                        conn.update(worksheet="Requests", data=pending_df.drop(pending_df.index[req_idx]))
                        st.rerun()
        except: pass

#--------------------
# Section 11: Logic (Deepthink & Thorough Think)
#--------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

if prompt := st.chat_input("Communicate..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    response = ""
    raw_data = ""

    # A. MATH
    response = run_math(prompt)

    # B. DATA GATHERING
    # 1. Check Context (Priority for Thorough Think)
    if not response and st.session_state.thorough_think and is_speak_role:
        try:
            c_df = conn.read(worksheet="Context", ttl="1s")
            topics = c_df['Topic'].fillna('').tolist()
            if topics:
                m, s = process.extractOne(prompt, topics, scorer=fuzz.token_sort_ratio)
                if s >= intel_level: raw_data = c_df[c_df['Topic'] == m].iloc[-1]['Meaning']
        except: pass

    # 2. Deepthink
    if not raw_data and not response and st.session_state.deepthink_enabled:
        with st.status("🧠 Deepthinking...", expanded=False):
            raw_data = run_deepthink(prompt, summarize=(is_admin_role and 'sport_mode' in locals() and sport_mode))
    
    # 3. Memory
    if not raw_data and not response:
        try:
            m_df = conn.read(worksheet="Memory", ttl="1s")
            qs = m_df['question'].fillna('').tolist()
            if qs:
                m, s = process.extractOne(prompt, qs, scorer=fuzz.token_sort_ratio)
                if s >= intel_level: raw_data = m_df[m_df['question'] == m].iloc[-1]['answer']
        except: pass

    # C. SYNTHESIS
    if raw_data:
        if st.session_state.thorough_think and is_speak_role:
            with st.status("🔬 Thorough Thinking...", expanded=False):
                tokens = re.findall(r'\b\w{5,}\b', raw_data.lower())
                response = f"### 🧪 SYNTHESIZED INSIGHT\n\n**Processed Context:** {', '.join(list(set(tokens))[:5])}...\n\n"
                response += f"Based on the cortex: {raw_data[:850]}..."
        else:
            response = raw_data

    # D. FALLBACK
    if not response:
        if st.session_state.waiting_for_answer:
            if is_speak_role:
                save_direct(st.session_state.last_question, prompt, conn)
                response = "⚡ **Cortex Updated.**"
            else:
                save_request(st.session_state.last_question, prompt, conn)
                response = "📝 **Lesson Queued.**"
            st.session_state.waiting_for_answer = False
        else:
            response = "I haven't learned that yet. **What is the answer?**"
            st.session_state.waiting_for_answer = True
            st.session_state.last_question = prompt

    # E. OUTPUT
    if response:
        he_t = get_hebrew(response) if st.session_state.hebrew_mode else ""
        full = response + (f"\n\n---\n<div class='rtl-container'>🇮🇱 {he_t}</div>" if he_t else "")
        with st.chat_message("assistant"):
            st.markdown(full, unsafe_allow_html=True)
            if st.session_state.voice_mode: show_voices(response, he_t)
        st.session_state.messages.append({"role": "assistant", "content": full})
