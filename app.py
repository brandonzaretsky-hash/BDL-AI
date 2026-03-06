import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fuzzywuzzy import fuzz, process
from deep_translator import GoogleTranslator
from gtts import gTTS
import io, re, wikipedia, wikipediaapi
from datetime import datetime

st.set_page_config(page_title="BDL-ai V5.2", layout="wide", page_icon="🤖")

if "messages" not in st.session_state: st.session_state.messages = []
if "waiting_for_answer" not in st.session_state: st.session_state.waiting_for_answer = False
if "last_question" not in st.session_state: st.session_state.last_question = ""

#--------------------
# Section 2: Sidebar & Access Control
#--------------------
with st.sidebar:
    st.title("🛡️ BDL Security")
    access_key = st.text_input("Access Key", type="password")

    # ROLE CHECKS
    is_speak_role = (access_key == "qwerty") # Super-Dev
    is_admin_role = (access_key == "admin") or is_speak_role # Admin
    
    # USER TOOLS
    st.markdown("### 🛠️ Basic Controls")
    intel_level = st.slider("🧠 Intelligence Slider", 50, 100, 85)
    hebrew_mode = st.toggle("🇮🇱 Hebrew Mode")
    voice_mode = st.toggle("🔊 Voice Response")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    # ADMIN APPROVAL PANEL
    if is_admin_role:
        st.markdown("---")
        st.markdown("### 👮 Admin Panel")
        sport_mode = st.toggle("🏒 Sport Mode")
        
        st.markdown("#### 📋 Pending Requests")
        conn = st.connection("gsheets", type=GSheetsConnection)
        try:
            pending_df = conn.read(worksheet="Requests", ttl="1s")
            if not pending_df.empty:
                st.dataframe(pending_df)
                req_idx = st.number_input("Row ID to Approve", 0, len(pending_df)-1, 0)
                if st.button("✅ Approve & Move to Memory"):
                    main_mem = conn.read(worksheet="Memory", ttl="1s")
                    approved = pending_df.iloc[[req_idx]][['question', 'answer']]
                    updated_main = pd.concat([main_mem, approved], ignore_index=True)
                    conn.update(worksheet="Memory", data=updated_main)
                    # Clean up request
                    new_pending = pending_df.drop(pending_df.index[req_idx])
                    conn.update(worksheet="Requests", data=new_pending)
                    st.success("Memory Authenticated!")
                    st.rerun()
            else: st.caption("No pending requests.")
        except: st.error("Add a 'Requests' tab to your Sheet.")

    # SUPER-DEV TOOLS
    if is_speak_role:
        st.markdown("---")
        st.markdown("### ⚡ Super-User Tools")
        st.session_state.is_speak_mode = st.toggle("🌐 Internet Deep-Scan", value=True)
    else:
        st.session_state.is_speak_mode = False

#--------------------
# Section 3: Data Write Functions
#--------------------
def save_direct(q, a):
    # For Super-Dev: Write straight to main memory
    df = conn.read(worksheet="Memory", ttl="1s")
    new_row = pd.DataFrame([{"question": q.lower(), "answer": a}])
    updated = pd.concat([df, new_row], ignore_index=True)
    conn.update(worksheet="Memory", data=updated)

def save_request(q, a):
    # For Users: Write to 'Requests' for Admin approval
    df = conn.read(worksheet="Requests", ttl="1s")
    new_req = pd.DataFrame([{
        "question": q.lower(), 
        "answer": a, 
        "user": "Standard User", 
        "timestamp": datetime.now().strftime("%H:%M")
    }])
    updated = pd.concat([df, new_req], ignore_index=True)
    conn.update(worksheet="Requests", data=updated)

#--------------------
# Section 4: Chat Display
#--------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"], unsafe_allow_html=True)

#--------------------
# Section 5: The Logic Brain (Read/Write/Search)
#--------------------
if prompt := st.chat_input("Communicate..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    response = ""
    hebrew_trans = ""

    # A. WRITE LOGIC (Teaching Mode)
    if st.session_state.waiting_for_answer:
        if is_speak_role:
            save_direct(st.session_state.last_question, prompt)
            response = "⚡ **Super-Dev Override:** Data written directly to Main Memory."
        else:
            save_request(st.session_state.last_question, prompt)
            response = "📝 **Lesson Logged:** Sent for Admin approval."
        st.session_state.waiting_for_answer = False

    # B. MATH ENGINE
    elif re.match(r"^[\d\+\-\*\/\(\)\s\.]+$", prompt.strip()):
        try: response = f"🔢 **Result:** {pd.eval(prompt)}"
        except: pass

    # C. KNOWLEDGE ENGINE (Read)
    if not response:
        # PATH 1: INTERNET (Super-Dev Speak Mode)
        if st.session_state.get('is_speak_mode'):
            wiki_link = wikipediaapi.Wikipedia('BDL-Bot/1.0', 'en')
            wants_summary = "(summary)" in prompt.lower() or (is_admin_role and sport_mode)
            CHAR_LIMIT = 1200 if wants_summary else 15000 
            clean_q = prompt.lower().replace("(summary)", "")
            for n in ['what is', 'who is', '?']: clean_q = clean_q.replace(n, "")
            
            with st.status("🚀 Knowledge Scan...", expanded=False) as status:
                try:
                    import wikipedia
                    s_results = wikipedia.search(clean_q.strip())
                    if s_results:
                        page = wiki_link.page(s_results[0])
                        if page.exists():
                            content = page.summary if wants_summary else page.text
                            response = f"### 📂 DATA REPORT: {page.title}\n\n" + content[:CHAR_LIMIT]
                except: response = "Internet Error."
                status.update(label="Complete!", state="complete")

        # PATH 2: LOCAL MEMORY (Standard Read)
        if not response:
            main_df = conn.read(worksheet="Memory", ttl="1s")
            questions = main_df['question'].fillna('').tolist()
            if questions:
                match, score = process.extractOne(prompt, questions, scorer=fuzz.token_sort_ratio)
                if score >= intel_level:
                    response = main_df[main_df['question'] == match].iloc[-1]['answer']

    # D. FALLBACK (Trigger Learning)
    if not response:
        response = "I haven't learned that yet. **What is the answer?**"
        st.session_state.waiting_for_answer = True
        st.session_state.last_question = prompt

    # E. TRANSLATION & FINAL OUTPUT
    if hebrew_mode and response:
        try: hebrew_trans = GoogleTranslator(source='auto', target='iw').translate(response[:800])
        except: pass

    if response:
        display = response
        if hebrew_trans: display += f"\n\n---\n<div style='direction: rtl; text-align: right;'>🇮🇱 {hebrew_trans}</div>"
        
        with st.chat_message("assistant"):
            st.markdown(display, unsafe_allow_html=True)
            if voice_mode:
                v1, v2 = st.columns(2)
                with v1:
                    t_en = gTTS(response[:3000], lang='en')
                    f_en = io.BytesIO(); t_en.write_to_fp(f_en); st.audio(f_en)
                if hebrew_trans:
                    with v2:
                        t_he = gTTS(hebrew_trans, lang='iw')
                        f_he = io.BytesIO(); t_he.write_to_fp(f_he); st.audio(f_he)
        st.session_state.messages.append({"role": "assistant", "content": display})
