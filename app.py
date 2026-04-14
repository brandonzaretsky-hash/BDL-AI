import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from fuzzywuzzy import fuzz, process
from deep_translator import GoogleTranslator
from gtts import gTTS
import io, re, wikipedia, wikipediaapi, time
from datetime import datetime

#--------------------
# Section 1: Setup, Styling, & Session State
#--------------------
st.set_page_config(page_title="BDL-ai V6.4 Master", layout="wide", page_icon="🤖")

st.markdown("""
    <style>
    .rtl-container { direction: rtl; text-align: right; font-family: 'Arial'; background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #444; }
    .stChatFloatingInputContainer { bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

if "messages" not in st.session_state: st.session_state.messages = []
if "waiting_for_answer" not in st.session_state: st.session_state.waiting_for_answer = False
if "last_question" not in st.session_state: st.session_state.last_question = ""
if "perf_data" not in st.session_state: st.session_state.perf_data = []
if "last_mem_count" not in st.session_state: st.session_state.last_mem_count = 0

#--------------------
# Section 2: Sidebar Security & Universal Controls
#--------------------
with st.sidebar:
    # UPDATED PANEL NAME
    st.title("🛡️ BDL.AI Setting Panel")
    access_key = st.text_input("Enter Access Key", type="password")

    is_speak_role = (access_key == "qwerty") # Super-Dev
    is_admin_role = (access_key == "admin") or is_speak_role # Admin
    
    st.markdown("### 🛠️ Global Settings")
    st.session_state.deepthink_enabled = st.toggle("🌐 Deepthink Mode (Internet)", value=False)
    intel_level = st.slider("🧠 Intelligence Level", 50, 100, 85)
    hebrew_mode = st.toggle("🇮🇱 Hebrew Mode")
    voice_mode = st.toggle("🔊 Voice Response")
    
    conn = st.connection("gsheets", type=GSheetsConnection)

    if is_admin_role:
        st.markdown("---")
        st.markdown("### 👮 Admin & Approval")
        sport_mode = st.toggle("🏒 Sport Mode")
        
        try:
            pending_df = conn.read(worksheet="Requests", ttl="1s")
            if not pending_df.empty:
                st.dataframe(pending_df, use_container_width=True)
                req_idx = st.number_input("ID to Manage", 0, len(pending_df)-1, 0)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Approve"):
                        main_mem = conn.read(worksheet="Memory", ttl="1s")
                        approved_row = pending_df.iloc[[req_idx]][['question', 'answer']]
                        conn.update(worksheet="Memory", data=pd.concat([main_mem, approved_row], ignore_index=True))
                        conn.update(worksheet="Requests", data=pending_df.drop(pending_df.index[req_idx]))
                        st.success("Lesson Approved!")
                        st.rerun()
                
                with col2:
                    # NEW DECLINE BUTTON
                    if st.button("❌ Decline"):
                        new_pending = pending_df.drop(pending_df.index[req_idx])
                        conn.update(worksheet="Requests", data=new_pending)
                        st.error("Lesson Deleted.")
                        st.rerun()
        except: 
            st.warning("⚠️ 'Requests' tab missing.")

    if st.button("🗑️ Clear Chat"):
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
# Section 4: Global Update Alert & History
#--------------------
try:
    current_mem = conn.read(worksheet="Memory", ttl="1s")
    current_count = len(current_mem)
    if st.session_state.last_mem_count == 0:
        st.session_state.last_mem_count = current_count
    
    if current_count > st.session_state.last_mem_count:
        st.success(f"🔔 **Update Alert:** {current_count - st.session_state.last_mem_count} new lesson(s) approved by Admin!")
        if st.button("Acknowledge Update"):
            st.session_state.last_mem_count = current_count
            st.rerun()
except: pass

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

#--------------------
# Section 5: Math Engine
#--------------------
def run_math(prompt):
    if re.match(r"^[\d\+\-\*\/\(\)\s\.]+$", prompt.strip()):
        try: return f"🔢 **Result:** {pd.eval(prompt)}"
        except: return None
    return None

#--------------------
# Section 6: Translation Engine
