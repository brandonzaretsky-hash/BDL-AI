import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fuzzywuzzy import fuzz, process
from deep_translator import GoogleTranslator
from gtts import gTTS
import io, re, wikipedia, wikipediaapi
from datetime import datetime

#--------------------
# Section 1: Setup, Styling, & Session State
#--------------------
st.set_page_config(page_title="BDL-ai V5.9 Master", layout="wide", page_icon="🤖")

# RTL and UI CSS
st.markdown("""
    <style>
    .rtl-container { direction: rtl; text-align: right; font-family: 'Arial'; background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #444; }
    .stChatFloatingInputContainer { bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "waiting_for_answer" not in st.session_state: st.session_state.waiting_for_answer = False
if "last_question" not in st.session_state: st.session_state.last_question = ""

#--------------------
# Section 2: Sidebar Security & Role Access
#--------------------
with st.sidebar:
    st.title("🛡️ BDL Access Control")
    access_key = st.text_input("Enter Access Key", type="password")

    # ROLE DEFINITION
    is_speak_role = (access_key == "qwerty") # Super-Dev
    is_admin_role = (access_key == "admin") or is_speak_role # Admin
    
    st.markdown("### 🛠️ Basic Controls")
    intel_level = st.slider("🧠 Intelligence Level", 50, 100, 85)
    hebrew_mode = st.toggle("🇮🇱 Hebrew Mode")
    voice_mode = st.toggle("🔊 Voice Response")
    
    if is_admin_role:
        st.markdown("---")
        st.markdown("### 👮 Admin Tools")
        sport_mode = st.toggle("🏒 Sport Mode")
        
        # Admin Approval Interface
        conn = st.connection("gsheets", type=GSheetsConnection)
        try:
            pending_df = conn.read(worksheet="Requests", ttl="1s")
            if not pending_df.empty:
                st.dataframe(pending_df)
                req_idx = st.number_input("ID to Approve", 0, len(pending_df)-1, 0)
                if st.button("✅ Approve Lesson"):
                    main_mem = conn.read(worksheet="Memory", ttl="1s")
                    approved = pending_df.iloc[[req_idx]][['question', 'answer']]
                    updated_main = pd.concat([main_mem, approved], ignore_index=True)
                    conn.update(worksheet="Memory", data=updated_main)
                    conn.update(worksheet="Requests", data=pending_df.drop(pending_df.index[req_idx]))
                    st.success("Authorized!")
                    st.rerun()
        except: st.warning("⚠️ 'Requests' tab missing.")

    # ONLY SUPER-DEV SEES OR USES SPEAK MODE
    if is_speak_role:
        st.markdown("---")
        st.markdown("### ⚡ Super-User")
        st.session_state.is_speak_mode = st.toggle("🌐 Internet Deep-Scan (Speak Mode)", value=True)
    else:
        # Force Speak Mode OFF for everyone else
        st.session_state.is_speak_mode = False

    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

#--------------------
# Section 3: Data Write Functions
#--------------------
def save_direct(q, a):
    df = conn.read(worksheet="Memory", ttl="1s")
    new_row = pd.DataFrame([{"question": q.lower(), "answer": a}])
    conn.update(worksheet="Memory", data=pd.concat([df, new_row], ignore_index=True))

def save_request(q, a):
    df = conn.read(worksheet="Requests", ttl="1s")
    new_req = pd.DataFrame([{"question": q.lower(), "answer": a, "user": "User", "timestamp": datetime.now().strftime("%H:%M")}])
    conn.update(worksheet="Requests", data=pd.concat([df, new_req], ignore_index=True))

#--------------------
# Section 4: Chat History Display
#--------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

#--------------------
# Section 5: Math Engine (Pre-Logic)
#--------------------
def run_math(prompt):
    if re.match(r"^[\d\+\-\*\/\(\)\s\.]+$", prompt.strip()):
        try: return f"🔢 **Result:** {pd.eval(prompt)}"
        except: return None
    return None

#--------------------
# Section 6: Translation Engine
#--------------------
def get_hebrew(text):
    try:
        return GoogleTranslator(source='auto', target='iw').translate(text[:800])
    except:
        return None

#--------------------
# Section 7: Voice Generation Engine
#--------------------
def play_voice(text, lang_code):
    try:
        tts = gTTS(text[:3000], lang=lang_code)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp
    except:
        return None

#--------------------
# Section 8: UI Layout Helpers
#--------------------
def show_dual_voice(en_text, he_text):
    v1, v2 = st.columns(2)
    with v1:
        en_fp = play_voice(en_text, 'en')
        if en_fp: st.audio(en_fp)
    if he_text:
        with v2:
            he_fp = play_voice(he_text, 'iw')
            if he_fp: st.audio(he_fp)

#--------------------
# Section 9: Internet Search Brain
#--------------------
def run_internet_scan(query, summarize=False):
    wiki_link = wikipediaapi.Wikipedia('BDL-Bot/1.0', 'en')
    wikipedia.set_lang("en")
    limit = 1200 if summarize else 15000
    
    clean_q = query.lower().replace("(summary)", "")
    for n in ['what is', 'who is', '?']: clean_q = clean_q.replace(n, "")
    
    try:
        s_results = wikipedia.search(clean_q.strip())
        if s_results:
            page = wiki_link.page(s_results[0])
            if page.exists():
                content = page.summary if summarize else page.text
                return f"### 📂 DATA REPORT: {page.title}\n\n" + content[:limit]
    except:
        return None
    return None

#--------------------
# Section 10: Local Memory Brain
#--------------------
def read_local_memory(prompt, threshold):
    try:
        df = conn.read(worksheet="Memory", ttl="1s")
        qs = df['question'].fillna('').tolist()
        if qs:
            match, score = process.extractOne(prompt, qs, scorer=fuzz.token_sort_ratio)
            if score >= threshold:
                return df[df['question'] == match].iloc[-1]['answer']
    except:
        return None
    return None

#--------------------
# Section 11: Logic - Sports and Hands-Brain
#--------------------
if prompt := st.chat_input("Communicate with BDL..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    response = ""
    hebrew_trans = ""

    # A. TEACHING MODE
    if st.session_state.waiting_for_answer:
        if is_speak_role:
            save_direct(st.session_state.last_question, prompt)
            response = "⚡ **Super-Dev Override:** Data saved to Main Memory."
        else:
            save_request(st.session_state.last_question, prompt)
            response = "📝 **Lesson Logged:** Sent for Admin approval."
        st.session_state.waiting_for_answer = False

    # B. MATH CHECK
    if not response:
        response = run_math(prompt)

    # C. HANDS-BRAIN (Internet & Sport Mode - RESTRICTED TO SUPER-DEV)
    # Even if sport_mode is on, it only searches if is_speak_role is True
    if not response and st.session_state.get('is_speak_mode') and is_speak_role:
        with st.status("🚀 Hands-Brain Scanning...", expanded=False) as status:
            # Admins can toggle Sport Mode, but Super-Dev must be logged in to run the scan
            summ = "(summary)" in prompt.lower() or sport_mode
            response = run_internet_scan(prompt, summarize=summ)
            status.update(label="Global Scan Complete!", state="complete")

    # D. LOCAL BRAIN (Memory Read)
    if not response:
        response = read_local_memory(prompt, intel_level)

    # E. FALLBACK
    if not response:
        response = "I haven't learned that yet. **What is the answer?**"
        st.session_state.waiting_for_answer = True
        st.session_state.last_question = prompt

    # F. FINAL OUTPUT
    if response:
        if hebrew_mode and "Result:" not in response:
            hebrew_trans = get_hebrew(response)

        full_display = response
        if hebrew_trans:
            full_display += f"\n\n---\n<div class='rtl-container'>🇮🇱 {hebrew_trans}</div>"

        with st.chat_message("assistant"):
            st.markdown(full_display, unsafe_allow_html=True)
            if voice_mode:
                show_dual_voice(response, hebrew_trans)
        
        st.session_state.messages.append({"role": "assistant", "content": full_display})

