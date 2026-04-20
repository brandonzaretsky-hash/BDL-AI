import streamlit as st
import pandas as pd
import random
import re
import io
import wikipedia
from streamlit_gsheets import GSheetsConnection
from fuzzywuzzy import fuzz, process
from deep_translator import GoogleTranslator
from gtts import gTTS

# --- 1. SYSTEM CONFIGURATION ---
st.set_page_config(page_title="BDL.AI NEXUS", layout="wide", page_icon="🧠")

# --- 2. DATABASE CONNECTION ---
# This connects to your specific Google Sheet using the secrets you set up
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 3. THE VISUAL CORTEX (THEME) ---
def apply_theme():
    st.markdown("""
        <style>
        .stApp { 
            background-color: #000; 
            background-image: radial-gradient(circle at 50% 50%, rgba(255, 0, 255, 0.1) 0%, rgba(0, 0, 0, 1) 70%); 
        }
        h1 { color: #FF00FF !important; text-shadow: 0 0 15px #FF00FF; text-align: center; font-weight: bold; }
        h2, h3 { color: #00FFFF !important; text-shadow: 0 0 10px #00FFFF; }
        p, span, div, li, label { color: #00ff41 !important; font-family: 'Courier New', monospace; text-shadow: 0 0 5px #00ff41; }
        section[data-testid="stSidebar"] { background-color: #051a05; border-right: 2px solid #FF8C00; }
        
        .stButton>button { 
            background-color: #000; 
            color: #00FFFF; 
            border: 1px solid #00FFFF; 
            box-shadow: 0 0 10px #00FFFF; 
            width: 100%; 
            transition: 0.3s;
        }
        .stButton>button:hover { 
            border: 1px solid #FF8C00; 
            color: #FF8C00; 
            box-shadow: 0 0 20px #FF8C00; 
        }

        .bot-card { 
            height: 250px; 
            display: flex; 
            flex-direction: column; 
            justify-content: center; 
            align-items: center; 
            text-align: center; 
            border: 2px solid #333; 
            border-radius: 15px; 
            background: rgba(0,0,0,0.5); 
            margin-bottom: 15px; 
        }
        .bot-card:hover { border: 1px solid #00ff41; box-shadow: 0 0 15px #00ff41; }
        
        .intel-counter { 
            font-size: 50px; 
            text-align: center; 
            border: 2px solid #00ff41; 
            padding: 15px; 
            border-radius: 15px; 
            margin-bottom: 30px; 
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.2);
        }
        </style>
        """, unsafe_allow_html=True)

# --- 4. SHARED UTILITIES ---

def show_voices(en_text, tr_text, lang_code, choice):
    """Generates audio for English and the translated language."""
    try:
        col1, col2 = st.columns(2)
        with col1:
            tts_en = gTTS(en_text[:1000], lang='en')
            fp_en = io.BytesIO()
            tts_en.write_to_fp(fp_en)
            st.audio(fp_en)
        if tr_text and choice != "None" and lang_code != "none":
            with col2:
                tts_tr = gTTS(tr_text[:1000], lang=lang_code)
                fp_tr = io.BytesIO()
                tts_tr.write_to_fp(fp_tr)
                st.audio(fp_tr)
    except: pass

def update_context(topic, meaning, status="Pending"):
    """Saves new data nodes to the GSheet for moderation."""
    try:
        df = conn.read(worksheet="Context", ttl="1s")
        new_row = pd.DataFrame([{"Topic": topic, "Meaning": meaning, "Status": status}])
        updated_df = pd.concat([df, new_row], ignore_index=True).drop_duplicates(subset=['Topic'], keep='last')
        conn.update(worksheet="Context", data=updated_df)
        return True
    except: return False

def get_intel_count():
    """Counts only the nodes you have approved."""
    try:
        c = conn.read(worksheet="Context", ttl="1s")
        return len(c[c['Status'] == 'Approved'])
    except: return 0

# --- 5. BOT LOGIC MODULES ---

def run_standard():
    st.title("🤖 BDL Standard")
    with st.sidebar:
        voice_on = st.toggle("Voice Synthesis")
        choice = st.selectbox("Language Bridge", ["None", "Hebrew", "Spanish", "French"])
        lang_map = {"Hebrew": "he", "Spanish": "es", "French": "fr", "None": "none"}
    
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("Accessing Standard Memory..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        df = conn.read(worksheet="Memory", ttl="1s")
        match, score = process.extractOne(p, df['question'].tolist(), scorer=fuzz.token_sort_ratio)
        ans = df[df['question'] == match].iloc[-1]['answer'] if score >= 85 else "Node data not found in local memory."
        
        trans = ""
        if choice != "None":
            trans = GoogleTranslator(source='auto', target=lang_map[choice]).translate(ans)
            ans_display = f"{ans}\n\n---\n**{choice}:** {trans}"
        else: ans_display = ans

        with st.chat_message("assistant"):
            st.markdown(ans_display)
            if voice_on: show_voices(ans, trans, lang_map[choice], choice)
        st.session_state.messages.append({"role": "assistant", "content": ans_display})

def run_think():
    st.title("🧠 BDL Think: Auto-Scout")
    st.caption("Auto-detects unknown words and scouts them from global nodes.")
    
    if p := st.chat_input("Enter a keyword or topic..."):
        with st.status("🔍 Scanning Cortex...", expanded=True) as status:
            all_df = conn.read(worksheet="Context", ttl="1s")
            # We scout for words that aren't already Approved
            approved = all_df[all_df['Status'] == 'Approved']
            topics = approved['Topic'].fillna('').tolist()
            
            match, score = process.extractOne(p, topics, scorer=fuzz.token_set_ratio)
            
            if score >= 85:
                ans = approved[approved['Topic'] == match].iloc[-1]['Meaning']
                status.update(label="Match found in Cortex.", state="complete")
            else:
                status.update(label=f"Topic '{p}' unknown. Accessing Wikipedia nodes...")
                try:
                    wikipedia.set_lang("en")
                    summary = wikipedia.summary(p, sentences=2)
                    # Automatically send to Moderation Deck as Pending
                    update_context(p.title(), summary, status="Pending")
                    ans = f"NEW DATA SCOUTED: {summary}\n\n⚠️ *Pending approval in Sidebar Moderation Deck.*"
                    status.update(label="New data node scouted and saved.", state="complete")
                except:
                    ans = "Error: Global nodes returned no data for this keyword."
                    status.update(label="Scout failed.", state="error")
            
            st.info(ans)

def run_onion():
    st.title("🧅 BDL Onion: Synthesis")
    if "onion_msgs" not in st.session_state: st.session_state.onion_msgs = []
    
    # Sidebar Dev Controls
    if st.session_state.get('is_dev', False):
        with st.sidebar:
            st.markdown("---")
            st.subheader("🛠️ ONION DEV BAR")
            if st.button("📊 VIEW APPROVED NODES"):
                all_df = conn.read(worksheet="Context", ttl="1s")
                st.dataframe(all_df[all_df['Status'] == 'Approved'])

    for m in st.session_state.onion_msgs:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("Communicate with the Onion..."):
        st.session_state.onion_msgs.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        with st.status("🧅 Peeling layers & synthesizing Approved nodes...", expanded=False):
            all_df = conn.read(worksheet="Context", ttl="1s")
            # ONLY use Approved data
            approved = all_df[all_df['Status'] == 'Approved']
            topics = approved['Topic'].fillna('').tolist()
            match, score = process.extractOne(p, topics, scorer=fuzz.token_set_ratio)
            
            if score >= 70:
                ans = approved[approved['Topic'] == match].iloc[-1]['Meaning']
            else:
                ans = "System 3: No approved node found. Use THINK mode to scout this topic."
            
        with st.chat_message("assistant"): st.markdown(ans)
        st.session_state.onion_msgs.append({"role": "assistant", "content": ans})

def run_dna():
    st.title("🧬 BDL DNA: Genealogy")
    target = st.text_input("Enter name for ancestral scan...")
    if st.button("EXECUTE SCAN") and target:
        with st.status("Searching deep lineage files..."):
            try:
                wikipedia.set_lang("en")
                summary = wikipedia.summary(target, sentences=3)
                st.markdown(f"### 🌳 Root Node: {target}")
                st.write(summary)
            except: st.error("No lineage data found for this entry.")

# --- 6. MAIN ROUTER & SIDEBAR MODERATION ---

apply_theme()
if "page" not in st.session_state: st.session_state.page = "Home"

with st.sidebar:
    st.title("🔑 Access Panel")
    if st.button("🌐 RETURN TO NEXUS HOME"): 
        st.session_state.page = "Home"
        st.rerun()
    
    key = st.text_input("Credentials", type="password")
    st.session_state.is_dev = (key == "qwerty")
    st.session_state.is_admin = (key in ["admin", "qwerty"])

    # THE MODERATION DECK
    if st.session_state.is_admin:
        st.markdown("---")
        st.subheader("🛡️ Moderation Deck")
        try:
            df = conn.read(worksheet="Context", ttl="1s")
            pending = df[df['Status'] == 'Pending']
            if not pending.empty:
                item = pending.iloc[0] # Focus on the oldest pending item
                st.info(f"**Topic:** {item['Topic']}\n\n**Data:** {item['Meaning']}")
                c1, c2 = st.columns(2)
                if c1.button("✅ Approve"):
                    df.loc[df['Topic'] == item['Topic'], 'Status'] = 'Approved'
                    conn.update(worksheet="Context", data=df)
                    st.success("Layer Approved!")
                    st.rerun()
                if c2.button("❌ Decline"):
                    df = df[df['Topic'] != item['Topic']] # Delete it
                    conn.update(worksheet="Context", data=df)
                    st.error("Layer Deleted.")
                    st.rerun()
            else:
                st.write("✅ Cortex is synchronized.")
        except: st.write("Waiting for GSheet Link...")

# --- PAGE ROUTING ---

if st.session_state.page == "Home":
    st.markdown("<h1>BDL.AI NEXUS GATEWAY</h1>", unsafe_allow_html=True)
    score = get_intel_count()
    st.markdown(f"<div class='intel-counter'><span>{score}</span><br><small>APPROVED NODES IN CORTEX</small></div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("<div class='bot-card'><h2>🤖</h2><h3>BDL</h3><p>Standard Memory</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE BDL"): st.session_state.page = "BDL"; st.rerun()
    with c2:
        st.markdown("<div class='bot-card'><h2>🧠</h2><h3>THINK</h3><p>Auto-Scout</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE THINK"): st.session_state.page = "Think"; st.rerun()
    with c3:
        st.markdown("<div class='bot-card'><h2>🧅</h2><h3>ONION</h3><p>Synthesis</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE ONION"):
            if st.session_state.is_dev: st.session_state.page = "Onion"; st.rerun()
            else: st.warning("Dev Key Required.")
    with c4:
        st.markdown("<div class='bot-card'><h2>🧬</h2><h3>DNA</h3><p>Genealogy</p></div>", unsafe_allow_html=True)
        if st.button("🔌 INITIALIZE DNA"): st.session_state.page = "DNA"; st.rerun()

elif st.session_state.page == "BDL": run_standard()
elif st.session_state.page == "Think": run_think()
elif st.session_state.page == "Onion": run_onion()
elif st.session_state.page == "DNA": run_dna()
