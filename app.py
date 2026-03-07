import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fuzzywuzzy import fuzz, process
from deep_translator import GoogleTranslator
from gtts import gTTS
import io, re, wikipedia, wikipediaapi
from datetime import datetime

# --- UI Configuration ---
st.set_page_config(page_title="BDL-ai V5.6 Master", layout="wide", page_icon="🤖")

# Right-to-Left Support for Hebrew and UI Styling
st.markdown("""
    <style>
    .rtl-container { direction: rtl; text-align: right; font-family: 'Arial'; background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #444; }
    .stChatFloatingInputContainer { bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session States
if "messages" not in st.session_state: st.session_state.messages = []
if "waiting_for_answer" not in st.session_state: st.session_state.waiting_for_answer = False
if "last_question" not in st.session_state: st.session_state.last_question = ""
#--------------------
#Section 2 Sidebar Securaty
#--------------------
with st.sidebar:
    st.title("🛡️ BDL Access Control")
    access_key = st.text_input("Enter Access Key", type="password")

    # ROLE IDENTIFICATION
    # Super-Dev (Internet/Direct Write): qwerty
    # Admin (Approval/Sport): admin
    is_speak_role = (access_key == "qwerty")
    is_admin_role = (access_key == "admin") or is_speak_role
    
    # --- LEVEL 1: USER CONTROLS (Always Visible) ---
    st.markdown("### 🛠️ Basic Controls")
    intel_level = st.slider("🧠 Intelligence Level", 50, 100, 85, help="Controls matching strictness.")
    hebrew_mode = st.toggle("🇮🇱 Hebrew Mode")
    voice_mode = st.toggle("🔊 Voice Response")
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    # --- LEVEL 2: ADMIN PANEL (admin or qwerty) ---
    if is_admin_role:
        st.markdown("---")
        st.markdown("### 👮 Admin & Approvals")
        sport_mode = st.toggle("🏒 Sport Mode", help="Summarizes NHL/Sports data.")
        
        # Connect to Sheets for Approval Logic
        conn = st.connection("gsheets", type=GSheetsConnection)
        try:
            pending_df = conn.read(worksheet="Requests", ttl="1s")
            if not pending_df.empty:
                st.dataframe(pending_df)
                req_idx = st.number_input("Select Row ID", 0, len(pending_df)-1, 0)
                if st.button("✅ Approve & Move to Memory"):
                    main_mem = conn.read(worksheet="Memory", ttl="1s")
                    approved_row = pending_df.iloc[[req_idx]][['question', 'answer']]
                    updated_main = pd.concat([main_mem, approved_row], ignore_index=True)
                    conn.update(worksheet="Memory", data=updated_main)
                    # Clean the request
                    new_pending = pending_df.drop(pending_df.index[req_idx])
                    conn.update(worksheet="Requests", data=new_pending)
                    st.success("Lesson Authorized!")
                    st.rerun()
            else: st.caption("No pending requests.")
        except: st.warning("⚠️ 'Requests' tab missing in Google Sheets.")

    # --- LEVEL 3: SUPER-DEV TOOLS (qwerty Only) ---
    if is_speak_role:
        st.markdown("---")
        st.markdown("### ⚡ Super-User Tools")
        st.session_state.is_speak_mode = st.toggle("🌐 Internet Deep-Scan", value=True)
        
        if st.button("🩺 Run Sheet Doctor"):
            st.info("🔍 Diagnostic: 'Memory' and 'Requests' tabs must exist.")
            try:
                m_check = conn.read(worksheet="Memory", ttl="1s")
                st.write("✅ Memory Tab: OK")
            except: st.write("❌ Memory Tab: MISSING")
            try:
                r_check = conn.read(worksheet="Requests", ttl="1s")
                st.write("✅ Requests Tab: OK")
            except: st.write("❌ Requests Tab: MISSING")
    else:
        st.session_state.is_speak_mode = False
#-------------------
#Section 3 Data logic Functions
#-------------------
def save_direct(q, a):
    """Direct Write for Super-Devs"""
    try:
        df = conn.read(worksheet="Memory", ttl="1s")
        new_entry = pd.DataFrame([{"question": q.lower(), "answer": a}])
        conn.update(worksheet="Memory", data=pd.concat([df, new_entry], ignore_index=True))
        st.success("⚡ Memory Saved Locally.")
    except:
        st.error("Write failed. Check sheet structure.")

def save_request(q, a):
    """Approval Request for Standard Users"""
    try:
        df = conn.read(worksheet="Requests", ttl="1s")
        new_req = pd.DataFrame([{
            "question": q.lower(), 
            "answer": a, 
            "user": "User", 
            "timestamp": datetime.now().strftime("%H:%M")
        }])
        conn.update(worksheet="Requests", data=pd.concat([df, new_req], ignore_index=True))
    except:
        st.error("Requests tab not found. Contact Super-Dev.")
#-------------------
#Section 4 Chat intercation and Logic Brain
#-------------------
# Display Message History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

if prompt := st.chat_input("Communicate..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    response = ""
    hebrew_trans = ""

    # A. TEACHING MODE (Requesting Logic)
    if st.session_state.waiting_for_answer:
        # Check roles for saving
        if is_speak_role:
            save_direct(st.session_state.last_question, prompt)
            response = "⚡ Super-Dev: Data stored in main brain."
        else:
            # THIS IS THE REQUEST PART: Saves to 'Requests' tab
            save_request(st.session_state.last_question, prompt)
            response = "📝 User: Answer sent for Admin approval."
        st.session_state.waiting_for_answer = False

    # B. KNOWLEDGE ENGINE (Reading Logic)
    if not response:
        # 1. First check if it's a Math problem
        if re.match(r"^[\d\+\-\*\/\(\)\s\.]+$", prompt.strip()):
            try: response = f"🔢 **Result:** {pd.eval(prompt)}"
            except: pass

    if not response:
        # 2. Local Memory Read (SPECIFY THE WORKSHEET)
        try:
            # WE MUST TELL IT TO READ 'Memory'
            main_df = conn.read(worksheet="Memory", ttl="1s")
            questions = main_df['question'].fillna('').tolist()
            
            # Use the Intelligence Slider
            match, score = process.extractOne(prompt, questions, scorer=fuzz.token_sort_ratio)
            
            if score >= intel_level:
                response = main_df[main_df['question'] == match].iloc[-1]['answer']
        except Exception as e:
            st.error(f"Read Error: {e}")

    # C. FALLBACK (Trigger the Request)
    if not response:
        response = "I haven't learned that yet. **What is the answer?**"
        st.session_state.waiting_for_answer = True
        st.session_state.last_question = prompt

    # D. OUTPUT
    if response:
        with st.chat_message("assistant"):
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
