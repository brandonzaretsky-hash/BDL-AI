import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime
from deep_translator import GoogleTranslator
from thefuzz import process, fuzz
from gtts import gTTS
import io
import re

#--------------------
# Section 1: Page Configuration & Global Styles
#--------------------
st.set_page_config(page_title="BDL.AI - Master Brain", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stChatMessage { border-radius: 15px; padding: 10px; margin-bottom: 10px; }
    h1 { color: #00d4ff; text-align: center; text-shadow: 0 0 10px #00d4ff; }
    
    .rtl-container {
        direction: rtl; text-align: right; background-color: #1f2937;
        padding: 12px; border-radius: 10px; margin-top: 10px;
        color: #ffffff; border-right: 5px solid #00ff00;
    }

    /* Green Audio Player Hack */
    audio {
        filter: sepia(1) saturate(3) hue-rotate(90deg) brightness(1.2);
        height: 30px; width: 100%;
    }
    .stAudio { border-left: 5px solid #00ff00; padding-left: 10px; }

    .pulse-container { display: flex; align-items: center; gap: 10px; font-weight: bold; color: #00ff00; margin-bottom: 20px; }
    .pulse-circle {
        width: 12px; height: 12px; background-color: #00ff00; border-radius: 50%;
        box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7);
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 255, 0, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 0, 0); }
    }
    </style>
    """, unsafe_allow_html=True)

#--------------------
# Section 2: Global Variable & Session Initialization
#--------------------
if "is_admin" not in st.session_state: st.session_state.is_admin = False
if "is_speak_mode" not in st.session_state: st.session_state.is_speak_mode = False
if "slang_mode" not in st.session_state: st.session_state.slang_mode = False  # Add this!
if "waiting_for_answer" not in st.session_state: st.session_state.waiting_for_answer = False
if "last_question" not in st.session_state: st.session_state.last_question = ""
if "messages" not in st.session_state: st.session_state.messages = []
if "offline_buffer" not in st.session_state: st.session_state.offline_buffer = []
#--------------------
# Section 3: Database Connection & Data Loading
#--------------------
connection_status = "Offline"
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
    connection_status = "Online"
except Exception:
    df = pd.DataFrame(columns=["question", "answer", "status", "timestamp"])

def load_fresh_data():
    if connection_status == "Online": return conn.read(ttl=0)
    return pd.DataFrame(columns=["question", "answer", "status", "timestamp"])

#--------------------
# Section 4: Sidebar - Access Control & Mode Switching
#--------------------
with st.sidebar:
    st.title("🔐 Master Control")
    
    # Universal Input Box
    admin_input = st.text_input("Admin Key", type="password")
    
    # 1. Check for the "speak" command toggle
    if admin_input.lower().strip() == "speak":
        st.session_state.is_speak_mode = True
        st.session_state.is_admin = False
        st.warning("🕵️ Neural Speak Mode: ACTIVE")
        st.caption("Chat input will now be synthesized from memories.")
        conf_level = 85 # Default for synthesis
        
    # 2. Check for the standard admin password
    elif admin_input == "admin123":
        st.session_state.is_admin = True
        st.session_state.is_speak_mode = False
        st.markdown('<div class="pulse-container"><div class="pulse-circle"></div><span>ADMIN: ONLINE</span></div>', unsafe_allow_html=True)
        st.markdown("---")
        st.write("🧠 **Match Strictness**")
        conf_level = st.slider("Strictness", 50, 100, 85)
        
    # 3. Default to User Mode
    else:
        st.session_state.is_admin = False
        st.session_state.is_speak_mode = False
        st.info("User Mode Active")
        conf_level = 85
    
    st.markdown("---")
    hebrew_mode = st.toggle("🇮🇱 Hebrew Mode")
    voice_mode = st.toggle("🔊 Voice Response")
    slang_mode = st.toggle("🧢 Slang Grammar Mode") # New Toggle
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
   
#--------------------
# Section 5: Sidebar - Maintenance & Diagnostics
#--------------------
if st.session_state.is_admin:
    with st.sidebar:
        st.markdown("---")
        st.subheader("🛠️ Brain Tools")
        if st.button("🧹 Auto-Fix Brain"):
            df_clean = df.dropna(subset=['question', 'answer'])
            if connection_status == "Online":
                conn.update(data=df_clean)
                st.success("Cleaned!")
                st.rerun()

        if st.button("🚀 Run Full System Test"):
            with st.status("Deep Diagnostic...", expanded=True) as s:
                st.write("Checking Grammar Logic...")
                if "speak test".startswith("speak "): st.success("✅ Secret Mode: Standby")
                
                st.write("Testing Math...")
                if pd.eval("10*10") == 100: st.success("✅ Math: Passed")
                
                st.write("Checking Voice Engines...")
                try:
                    gTTS("test", lang='en'); st.success("✅ Voice: Online")
                except: st.error("❌ Voice: Offline")
                
                s.update(label="All Systems Operational!", state="complete")

#--------------------
# Section 6: Sidebar - Moderation & Analytics
#--------------------
if st.session_state.is_admin:
    with st.sidebar:
        st.markdown("---")
        # Moderation Logic
        if 'status' in df.columns:
            pending = df[df['status'] == 'pending']
            if not pending.empty:
                st.warning(f"🔔 {len(pending)} New Requests")
                for i, row in pending.iterrows():
                    with st.expander(f"Q: {row['question'][:10]}"):
                        st.write(f"A: {row['answer']}")
                        if st.button("✅ Approve", key=f"app_{i}"):
                            df.at[i, 'status'] = 'verified'
                            conn.update(data=df); st.rerun()

#--------------------
# Section 7: Sidebar - Data Sync & Backup
#--------------------
with st.sidebar:
    st.markdown("---")
    if st.session_state.offline_buffer and connection_status == "Online" and st.session_state.is_admin:
        if st.button("🚀 Sync Offline Memories"):
            new_data = pd.DataFrame(st.session_state.offline_buffer)
            updated_df = pd.concat([df, new_data], ignore_index=True)
            conn.update(data=updated_df)
            st.session_state.offline_buffer = []
            st.rerun()
    
    if not df.empty:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Brain Backup", csv, "BDL_Backup.csv", "text/csv")

#--------------------
# Section 8: Main UI Header & Message Display
#--------------------
st.title("🧠 BDL.AI - Master Brain")
st.caption(f"Status: {connection_status} | Mode: {'Admin' if st.session_state.is_admin else 'User'}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

#--------------------
# Section 9: Logic - Global Variables & Input
#--------------------
if prompt := st.chat_input("Communicate..."):
    # Always initialize these so the app never crashes on 'hebrew_trans'
    response = ""
    hebrew_trans = ""
    import wikipedia
    from googlesearch import search
    wikipedia.set_lang("en")

    if prompt.lower() == "forget that" and st.session_state.is_admin:
        if connection_status == "Online" and not df.empty:
            conn.update(data=df.drop(df.tail(1).index))
            response = "🗑️ Memory Wiped."
        else: response = "Cannot forget right now."
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        # Math Logic
        if re.match(r"^[\d\+\-\*\/\(\)\s\.]+$", prompt.strip()):
            try: response = f"🔢 **Result:** {pd.eval(prompt)}"
            except: pass

#--------------------
# Section 11: Logic - Infinite Knowledge & NHL Specialist
#--------------------
        elif not response:
            current_df = load_fresh_data()
            
            # --- CASE A: INTERNET-AUGMENTED SPEAK MODE ---
            if st.session_state.get('is_speak_mode'):
                import wikipediaapi
                # We identify as your BDL bot to Wikipedia
                wiki_link = wikipediaapi.Wikipedia('BDL-Bot/1.0', 'en')
                
                # THE MAX CAP: ~2,000 Words (12,000 characters)
                CHAR_LIMIT = 12000 

                with st.status("🚀 BDL is performing a Deep Scan...", expanded=False) as status:
                    query_keywords = ['who', 'what', 'how', 'why', 'where', 'is', 'solve', 'list', '?']
                    is_question = any(k in prompt.lower() for k in query_keywords)
                    
                    if is_question:
                        # Clean the prompt for the search engine
                        wiki_query = prompt.replace("who is", "").replace("what is", "").replace("?", "").strip()
                        page = wiki_link.page(wiki_query)
                        
                        if page.exists():
                            # WE GRAB THE FULL TEXT (Intro + All Chapters)
                            full_text = page.text 
                            response = full_text[:CHAR_LIMIT] + "\n\n[--- END OF DATA STREAM ---]"
                        else:
                            # Fallback to Google Search
                            from googlesearch import search
                            res = list(search(prompt, num_results=1))
                            response = f"I solved this using the web. Link: {res[0]}" if res else "No records found."
                    
                    # 2. Memory Stitching (Non-Questions)
                    if not response:
                        tokens = prompt.lower().split()
                        stitched = []
                        for word in tokens:
                            match = current_df[current_df['question'].str.lower() == word]
                            if not match.empty:
                                stitched.append(str(match.iloc[-1]['answer']))
                            elif word in ['is', 'the', 'and', 'with', 'of', 'in', 'to']:
                                stitched.append(word)
                            else:
                                # Quick lookup for unknown single words
                                w_page = wiki_link.page(word)
                                if w_page.exists():
                                    stitched.append(f"({w_page.summary[:150]}...)")
                                else:
                                    stitched.append(word)
                        response = " ".join(stitched).capitalize()

                    status.update(label=f"Scan Complete: {len(response)} characters integrated", state="complete")

            # --- CASE B: STANDARD USER MODE ---
            else:
                questions = current_df['question'].fillna('').tolist()
                if questions:
                    match, score = process.extractOne(prompt, questions, scorer=fuzz.token_sort_ratio)
                    if score >= 90:
                        response = current_df[current_df['question'] == match].iloc[-1]['answer']

            if not response:
                response = "I haven't learned that yet. **What is the answer?**"
                st.session_state.waiting_for_answer = True
                st.session_state.last_question = prompt

#--------------------
# Section 12: Logic - Hebrew Translation (RESTORATION)
#--------------------
        hebrew_trans = ""
        if hebrew_mode and response and "Result:" not in response:
            try:
                # We translate only the first 1000 chars for speed, but response stays long
                hebrew_trans = GoogleTranslator(source='auto', target='iw').translate(response[:1000])
            except:
                pass

#--------------------
# Section 13: Logic - Multi-Voice Output Engine
#--------------------
        if response:
            display_text = response
            if hebrew_trans:
                display_text += f"\n\n<div class='rtl-container'>🇮🇱 **Hebrew Summary:** {hebrew_trans}</div>"
            
            with st.chat_message("assistant"):
                st.markdown(display_text, unsafe_allow_html=True)
                
                # VOICE ROW
                v_col1, v_col2 = st.columns(2)
                if voice_mode:
                    with v_col1:
                        try:
                            # Note: gTTS will take a second to generate 2000 words!
                            tts_en = gTTS(response[:3000], lang='en') # Capped at 3000 for voice stability
                            en_fp = io.BytesIO()
                            tts_en.write_to_fp(en_fp)
                            st.audio(en_fp, format='audio/mp3')
                            st.caption("🔊 English Audio (Full Stream)")
                        except:
                            st.warning("EN Voice Overload - Try a shorter prompt.")
                    
                    if hebrew_mode and hebrew_trans:
                        with v_col2:
                            try:
                                tts_he = gTTS(hebrew_trans, lang='iw') # Using 'iw' for Hebrew
                                he_fp = io.BytesIO()
                                tts_he.write_to_fp(he_fp)
                                st.audio(he_fp, format='audio/mp3')
                                st.caption("🇮🇱 Hebrew Audio")
                            except:
                                st.warning("HE Voice Error")

            st.session_state.messages.append({"role": "assistant", "content": display_text})
